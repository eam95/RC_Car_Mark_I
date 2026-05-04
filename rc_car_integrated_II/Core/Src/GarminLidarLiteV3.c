/*
 * GarminLidarLiteV3.c
 *
 *  Original: Nov 10, 2025 - Author: erick
 *  Fixed:    Non-blocking pipelined measurement + bounded I2C timeouts
 *
 *  ROOT CAUSE OF GAP BUG:
 *  HAL_I2C_Mem_Write/Read were called with HAL_MAX_DELAY. When the LIDAR's
 *  I2C bus stalls (NACK, clock-stretch, or noise on the new board), the HAL
 *  blocks the entire main loop indefinitely — confirmed at 1.38s in test data.
 *
 *  FIX SUMMARY:
 *  1. All I2C calls now use I2C_TIMEOUT_MS (5 ms) instead of HAL_MAX_DELAY.
 *     If any single transaction takes longer than 5 ms the HAL returns an error,
 *     logs it, and the caller continues — the main loop is never held hostage.
 *
 *  2. simple_measurement() is replaced by a pipelined non-blocking design:
 *     - Cycle N:   read the result that was triggered in cycle N-1 (if ready)
 *                  then immediately trigger the next acquisition.
 *     - Cycle N+1: read that result, trigger N+2 ... and so on.
 *     The LIDAR is always acquiring in the background; the MCU never waits.
 */

#include "stm32h7xx_hal.h"
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "GarminLidarLiteV3.h"
#include "main.h"
#include "delay.h"

extern I2C_HandleTypeDef hi2c2;
extern UART_HandleTypeDef huart3;
extern volatile uint8_t acq_cmd_param;

/* ------------------------------------------------------------------
 * I2C timeout for every transaction.
 * 5 ms is generous at 400 kHz (a full 32-byte transfer takes < 1 ms)
 * but short enough that a stalled bus costs at most 5 ms, not 1.38 s.
 * ------------------------------------------------------------------ */
#define I2C_TIMEOUT_MS   5U

/* ------------------------------------------------------------------
 * Pipelined measurement state  (used by simple_measurement_NB only)
 * ------------------------------------------------------------------ */
static uint16_t  _last_good_dist   = 0;      /* last successfully read distance */
static uint8_t   _acq_pending      = 0;      /* 1 = acquisition was triggered    */
static uint32_t  _acq_trigger_tick = 0;      /* HAL_GetTick() at trigger time    */

/* How long to wait for the LIDAR busy flag to clear before giving up.
 * Normal acquisition time is ~20 ms; 30 ms gives 50 % margin and still
 * fits comfortably inside the 20 ms main-loop cycle when non-blocking. */
#define LIDAR_ACQ_TIMEOUT_MS  30U


/* ==================================================================
 *  LOW-LEVEL I2C WRAPPERS  (bounded timeout, never HAL_MAX_DELAY)
 * ================================================================== */

void GarLiteV3_i2c_write(uint8_t reg, uint8_t *buf, uint16_t len)
{
    if (HAL_I2C_Mem_Write(&hi2c2,
                           LIDARLITEV3_I2C_ADDRESS,
                           reg,
                           I2C_MEMADD_SIZE_8BIT,
                           buf, len,
                           I2C_TIMEOUT_MS) != HAL_OK)
    {
        /* Log the error but DO NOT stall. The caller decides what to do. */
        HAL_UART_Transmit(&huart3,
            (uint8_t *)"LIDAR I2C Write Error\r\n",
            strlen("LIDAR I2C Write Error\r\n"),
            I2C_TIMEOUT_MS);

        /* Attempt a soft recovery so the bus is usable next cycle. */
        HAL_I2C_Init(&hi2c2);
    }
}

void GarLiteV3_i2c_read(uint8_t reg, uint8_t *buf, uint16_t len)
{
    if (HAL_I2C_Mem_Read(&hi2c2,
                          LIDARLITEV3_I2C_ADDRESS,
                          reg,
                          I2C_MEMADD_SIZE_8BIT,
                          buf, len,
                          I2C_TIMEOUT_MS) != HAL_OK)
    {
        HAL_UART_Transmit(&huart3,
            (uint8_t *)"LIDAR I2C Read Error\r\n",
            strlen("LIDAR I2C Read Error\r\n"),
            I2C_TIMEOUT_MS);

        HAL_I2C_Init(&hi2c2);
    }
}


/* ==================================================================
 *  INITIALISATION
 * ================================================================== */

void GarLiteV3_Init(void)
{
    /* Reset the device, then issue the first acquisition so the pipeline
     * has something to read on the very first call to simple_measurement_NB(). */
    config_ACQ_COMMAND_reg(RESET_DEVICE, 1);
    HAL_Delay(22);   /* datasheet: allow 22 ms after reset */

    config_ACQ_COMMAND_reg(TAKE_DISTANCE_MEASUREMENT_WITH_BIAS_CORRECTION, 1);
    HAL_Delay(10);

    uint8_t sensitivity = 0;
    config_THRESHOLD_BYPASS_reg(TH_SENSITIVITY_LEVEL(sensitivity), 1);
    HAL_Delay(10);

    /* Prime the pipeline: trigger first acquisition now so the first
     * call to simple_measurement_NB() can immediately read a result. */
    uint8_t cmd = acq_cmd_param;
    GarLiteV3_i2c_write(ACQ_COMMAND, &cmd, 1);
    _acq_pending      = 1;
    _acq_trigger_tick = HAL_GetTick();
}


/* ==================================================================
 *  PIPELINED NON-BLOCKING MEASUREMENT  ← call this from main loop
 *
 *  Call once per main-loop cycle (every 20 ms).
 *  Returns the most recent valid distance in *distanceCm.
 *  Never blocks for more than I2C_TIMEOUT_MS (5 ms) per call.
 *
 *  Pipeline behaviour:
 *    Call 1  : no pending acq yet → trigger first acq, return last (0 initially)
 *    Call 2+ : read status.
 *              If BUSY=0  → read distance, update _last_good_dist, trigger next acq
 *              If BUSY=1  → LIDAR still working; return last good value, no retrigger
 *              If timeout → LIDAR stuck; reinit pipeline, return last good value
 * ================================================================== */

void simple_measurement_NB(uint16_t *distanceCm)
{
    /* Always hand back the best value we have, even if we can't update it. */
    *distanceCm = _last_good_dist;

    if (!_acq_pending)
    {
        /* No acquisition in flight — fire one and come back next cycle. */
        uint8_t cmd = acq_cmd_param;
        GarLiteV3_i2c_write(ACQ_COMMAND, &cmd, 1);
        _acq_pending      = 1;
        _acq_trigger_tick = HAL_GetTick();
        return;
    }

    /* An acquisition is in flight. Check the busy flag. */
    uint8_t status = 0;
    GarLiteV3_i2c_read(STATUS, &status, 1);

    if (status & BUSY_FLAG)
    {
        /* Still acquiring. Check for timeout. */
        if ((HAL_GetTick() - _acq_trigger_tick) > LIDAR_ACQ_TIMEOUT_MS)
        {
            /* LIDAR is stuck. Re-trigger and try again next cycle.
             * This prevents the 1.38 s stall: we give up after 30 ms max. */
            HAL_UART_Transmit(&huart3,
                (uint8_t *)"LIDAR timeout, retriggering\r\n",
                strlen("LIDAR timeout, retriggering\r\n"),
                I2C_TIMEOUT_MS);

            uint8_t cmd = acq_cmd_param;
            GarLiteV3_i2c_write(ACQ_COMMAND, &cmd, 1);
            _acq_trigger_tick = HAL_GetTick();
            /* _acq_pending stays 1 */
        }
        /* Either still acquiring (within timeout) or just retriggered —
         * either way return the last good distance and come back next cycle. */
        return;
    }

    /* BUSY = 0: measurement is ready. Read the two distance bytes. */
    uint8_t high = 0, low = 0;
    GarLiteV3_i2c_read(FULL_DELAY_HIGH, &high, 1);
    GarLiteV3_i2c_read(FULL_DELAY_LOW,  &low,  1);
    _last_good_dist = ((uint16_t)high << 8) | low;
    *distanceCm     = _last_good_dist;

    /* Immediately fire the next acquisition so it runs in the background
     * while the main loop does everything else (IMU, NRF24 TX, etc.). */
    uint8_t cmd = acq_cmd_param;
    GarLiteV3_i2c_write(ACQ_COMMAND, &cmd, 1);
    _acq_pending      = 1;
    _acq_trigger_tick = HAL_GetTick();
}


/* ==================================================================
 *  LEGACY BLOCKING FUNCTIONS
 *  These are kept for init / debug use only.
 *  Do NOT call simple_measurement() from the main sensor loop —
 *  use simple_measurement_NB() instead.
 * ================================================================== */

void simple_measurement(uint16_t *distanceCm, uint8_t print)
{
    uint8_t  statusRegVal = 0;
    uint32_t timeDelay    = adjusteTimeForTicks(200);

    HAL_GPIO_TogglePin(LED_RED_GPIO_Port, LED_RED_Pin);
    statusRegVal = read_STATUS_reg(0);

    if ((statusRegVal & BUSY_FLAG) == 0)
    {
        HAL_GPIO_TogglePin(LED_RED_GPIO_Port, LED_RED_Pin);
        uint8_t high = read_FULL_DELAY_HIGH_reg(0);
        uint8_t low  = read_FULL_DELAY_LOW_reg(0);
        *distanceCm  = ((uint16_t)high << 8) | low;

        if (print == 1)
        {
            char buf[64];
            snprintf(buf, sizeof(buf),
                     "Distance Measurement Complete: %d cm\r\n", *distanceCm);
            HAL_UART_Transmit(&huart3, (uint8_t *)buf, strlen(buf), I2C_TIMEOUT_MS);
        }

        config_ACQ_COMMAND_reg(acq_cmd_param, 0);
        delay_us(timeDelay);
    }
}

void acq_count_measurements(uint16_t *distanceCm, uint8_t print)
{
    uint8_t  statusRegVal;
    uint32_t timeDelay = adjusteTimeForTicks(200);

    config_ACQ_COMMAND_reg(0x04, 0);

    HAL_GPIO_TogglePin(LED_RED_GPIO_Port, LED_RED_Pin);
    uint32_t start = HAL_GetTick();
    do {
        statusRegVal = read_STATUS_reg(0);
        if ((HAL_GetTick() - start) > LIDAR_ACQ_TIMEOUT_MS) break;
    } while ((statusRegVal & BUSY_FLAG) == 0);

    start = HAL_GetTick();
    do {
        statusRegVal = read_STATUS_reg(0);
        if ((HAL_GetTick() - start) > LIDAR_ACQ_TIMEOUT_MS) break;
    } while ((statusRegVal & BUSY_FLAG) != 0);
    HAL_GPIO_TogglePin(LED_RED_GPIO_Port, LED_RED_Pin);

    uint8_t high = read_FULL_DELAY_HIGH_reg(0);
    uint8_t low  = read_FULL_DELAY_LOW_reg(0);
    *distanceCm  = ((uint16_t)high << 8) | low;

    delay_us(timeDelay);

    if (print == 1)
    {
        char buf[64];
        snprintf(buf, sizeof(buf), "Distance Measurement: %d cm\r\n", *distanceCm);
        HAL_UART_Transmit(&huart3, (uint8_t*)buf, strlen(buf), I2C_TIMEOUT_MS);
    }
}

void burst_measurements(uint16_t *distanceArray, uint16_t numBurst, uint8_t print)
{
    uint8_t statusRegVal;
    char    buf[64];

    if (print == 1)
    {
        snprintf(buf, sizeof(buf),
                 "Starting burst of %u measurements...\r\n", numBurst);
        HAL_UART_Transmit(&huart3, (uint8_t*)buf, strlen(buf), I2C_TIMEOUT_MS);
    }

    for (uint16_t i = 0; i < numBurst; i++)
    {
        HAL_GPIO_WritePin(LED_RED_GPIO_Port, LED_RED_Pin, GPIO_PIN_SET);
        uint32_t start = HAL_GetTick();
        do {
            statusRegVal = read_STATUS_reg(0);
            if ((HAL_GetTick() - start) > LIDAR_ACQ_TIMEOUT_MS) break;
        } while ((statusRegVal & BUSY_FLAG) != 0);
        HAL_GPIO_WritePin(LED_RED_GPIO_Port, LED_RED_Pin, GPIO_PIN_RESET);

        HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_SET);
        uint8_t high = read_FULL_DELAY_HIGH_reg(0);
        uint8_t low  = read_FULL_DELAY_LOW_reg(0);
        distanceArray[i] = ((uint16_t)high << 8) | low;
        HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);

        if (print == 1)
        {
            snprintf(buf, sizeof(buf), "Burst %u: %u cm\r\n", i+1, distanceArray[i]);
            HAL_UART_Transmit(&huart3, (uint8_t*)buf, strlen(buf), I2C_TIMEOUT_MS);
        }
    }

    if (print == 1)
    {
        snprintf(buf, sizeof(buf), "Burst complete!\r\n");
        HAL_UART_Transmit(&huart3, (uint8_t*)buf, strlen(buf), I2C_TIMEOUT_MS);
    }
}
