/*
 * GarminLidarLiteV3.h
 *
 *  Original: Nov 9, 2025 - Author: erick
 *  Fixed:    Added simple_measurement_NB() declaration
 */

#ifndef INC_GARMINLIDARLITEV3_H_
#define INC_GARMINLIDARLITEV3_H_

#include "main.h"

/* ====================================================================
 *  I2C ADDRESS
 * ==================================================================== */
#define LIDARLITEV3_I2C_ADDRESS       (0x62 << 1)

/* ====================================================================
 *  REGISTER ADDRESSES
 * ==================================================================== */
#define ACQ_COMMAND       0x00
#define STATUS            0x01
#define SIG_COUNT_VAL     0x02
#define ACQ_CONFIG_REG    0x04
#define VELOCITY          0x09
#define PEAK_CORR         0x0C
#define NOISE_PEAK        0x0D
#define SIGNAL_STRENGTH   0x0E
#define FULL_DELAY_HIGH   0x0F
#define FULL_DELAY_LOW    0x10
#define OUTER_LOOP_COUNT  0x11
#define REF_COUNT_VAL     0x12
#define LAST_DELAY_HIGH   0x14
#define LAST_DELAY_LOW    0x15
#define UNIT_ID_HIGH      0x16
#define UNIT_ID_LOW       0x17
#define I2C_ID_HIGH       0x18
#define I2C_ID_LOW        0x19
#define I2C_SEC_ADDR      0x1A
#define THRESHOLD_BYPASS  0x1C
#define I2C_CONFIG        0x1E
#define COMMAND           0x40
#define MEASURE_DELAY     0x45
#define PEAK_BCK          0x4C
#define CORR_DATA         0x52
#define CORR_DATA_SIGN    0x53
#define ACQ_SETTINGS      0x5D
#define POWER_CONTROL     0x65

/* ====================================================================
 *  ACQ_COMMAND  (0x00)
 * ==================================================================== */
#define TAKE_DISTANCE_MEASUREMENT_WITH_BIAS_CORRECTION    0x04
#define TAKE_DISTANCE_MEASUREMENT_NO_BIAS_CORRECTION      0x03
#define RESET_DEVICE                                      0x00

/* ====================================================================
 *  STATUS  (0x01)
 * ==================================================================== */
#define PROCESS_ERROR_FLAG      0x40
#define HEALTH_FLAG             0x20
#define SECONDARY_RETURN_FLAG   0x10
#define INVALID_SIGNAL_FLAG     0x08
#define SIGNAL_OVERFLOW_FLAG    0x04
#define REFERENCE_OVERFLOW_FLAG 0x02
#define BUSY_FLAG               0x01

/* ====================================================================
 *  ACQ_CONFIG_REG  (0x04)
 * ==================================================================== */
#define ENABLE_REFERENCE_PROCESS    0x00
#define DISABLE_REFERENCE_PROCESS   0x40
#define ENABLE_MEASURE_DELAY        0x20
#define DISABLE_MEASURE_DELAY       0x00
#define ENABLE_REFERENCE_FILTER     0x10
#define DISABLE_REFERENCE_FILTER    0x00
#define ENABLE_QUICK_TERMINATION    0x08
#define DISABLE_QUICK_TERMINATION   0x00
#define ENABLE_REFERENCE_ACQ_COUNT  0x04
#define DISABLE_REFERENCE_ACQ_COUNT 0x00
#define DEFAULT_PWM_Mode            0x00
#define STATUS_OUTPUT_MODE          0x01
#define FIXED_DELAY_PWM_MODE        0x02
#define OSCILLATOR_OUTPUT_MODE      0x03

/* ====================================================================
 *  OUTER_LOOP_COUNT  (0x11)
 * ==================================================================== */
#define SINGLE_MEASUREMENT   0x01
#define CONT_MEASUREMENT     0xFF

/* ====================================================================
 *  THRESHOLD_BYPASS  (0x1C)
 * ==================================================================== */
#define TH_DEFAULT          0x00
#define TH_HIGH_SENSITIVITY 0x20
#define TH_LOW_SENSITIVITY  0x60
#define TH_SENSITIVITY_LEVEL(level)  ((level) & 0xFF)

/* ====================================================================
 *  I2C_CONFIG  (0x1E)
 * ==================================================================== */
#define I2C_RESPOND_TO_DEFAULT_AND_CUSTOM  0x00
#define I2C_RESPOND_TO_CUSTOM_ONLY         0x08

/* ====================================================================
 *  COMMAND  (0x40)
 * ==================================================================== */
#define TEST_MODE_ENABLE  0x07
#define TEST_MODE_DISABLE 0x00

/* ====================================================================
 *  POWER_CONTROL  (0x65)
 * ==================================================================== */
#define DEVICE_SLEEP              0x04
#define DEVICE_AWAKE              0x00
#define ENABLE_RECEIVER_CIRCUIT   0x01
#define DISABLE_RECEIVER_CIRCUIT  0x00

/* ====================================================================
 *  ACCESS  (0x5D)
 * ==================================================================== */
#define ACCESS_CORR_MEM_BANK    0xC0
#define NO_ACCESS_CORR_MEM_BANK 0x00


/* ====================================================================
 *  FUNCTION PROTOTYPES
 * ==================================================================== */

/* --- Low-level I2C (bounded timeout, never HAL_MAX_DELAY) --- */
void    GarLiteV3_i2c_write(uint8_t reg, uint8_t *buf, uint16_t len);
void    GarLiteV3_i2c_read (uint8_t reg, uint8_t *buf, uint16_t len);

/* --- Register config / read helpers (unchanged API) --- */
void    config_ACQ_COMMAND_reg(uint8_t command, uint8_t print);
uint8_t read_ACQ_COMMAND_reg(void);
void    print_config_ACQ_COMMAND_reg(void);

uint8_t read_STATUS_reg(uint8_t print);
void    print_STATUS_reg(uint8_t regval);

void    config_SIG_COUNT_VAL_reg(uint8_t sigCountVal, uint8_t print);
uint8_t read_SIG_COUNT_VAL_reg(uint8_t print);

void    config_ACQ_CONFIG_REG(uint8_t RefProcess, uint8_t delayMode,
                               uint8_t RefFilter, uint8_t QuickTermination,
                               uint8_t AcqCount, uint8_t PinFunc, uint8_t print);
void    print_config_ACQ_CONFIG_REG(void);

uint8_t read_VELOCITY_reg(uint8_t print);
uint8_t read_PEAK_CORR_reg(uint8_t print);
uint8_t read_NOISE_PEAK_reg(uint8_t print);
uint8_t read_SIGNAL_STRENGTH_reg(uint8_t print);
uint8_t read_FULL_DELAY_HIGH_reg(uint8_t print);
uint8_t read_FULL_DELAY_LOW_reg(uint8_t print);

void    config_OUTER_LOOP_COUNT_reg(uint8_t count, uint8_t print);
uint8_t read_REF_COUNT_VAL_reg(uint8_t print);
uint8_t read_LAST_DELAY_HIGH_reg(uint8_t print);
uint8_t read_LAST_DELAY_LOW_reg(uint8_t print);
void    read_UNIT_ID_HIGH_reg(uint8_t print);
void    read_UNIT_ID_LOW_reg(uint8_t print);
void    read_I2C_ID_HIGH_reg(uint8_t print);
void    read_I2C_ID_LOW_reg(uint8_t print);
void    read_I2C_SEC_ADDR_reg(uint8_t print);

void    config_THRESHOLD_BYPASS_reg(uint8_t sensitivity, uint8_t print);
void    config_COMMAND_reg(uint8_t command, uint8_t print);
void    config_MEASURE_DELAY_reg(uint8_t delay, uint8_t print);

uint8_t read_PEAK_BCK_reg(uint8_t print);
uint8_t read_CORR_DATA_reg(uint8_t print);
uint8_t read_CORR_DATA_SIGN_reg(uint8_t print);

void    config_ACQ_SETTINGS_reg(uint8_t bankAccess, uint8_t print);
void    config_POWER_CONTROL_reg(uint8_t wakeMode, uint8_t receiverCircuit,
                                  uint8_t print);

/* --- High-level measurement functions --- */
void    GarLiteV3_Init(void);

/*
 * simple_measurement_NB() — NON-BLOCKING pipelined measurement.
 *
 * Call once per main-loop cycle. On each call it either:
 *   a) reads the result of the previous acquisition and fires the next one, or
 *   b) checks if the LIDAR is still busy (returns last good value, no wait), or
 *   c) detects a timeout (>30 ms) and re-triggers without stalling.
 *
 * Maximum time spent inside this function per call: I2C_TIMEOUT_MS (5 ms).
 * Replace all calls to simple_measurement() in the sensor loop with this.
 */
void    simple_measurement_NB(uint16_t *distanceCm);

/*
 * simple_measurement() — kept for debug/init only.
 * DO NOT call from the main sensor loop; use simple_measurement_NB() instead.
 */
void    simple_measurement(uint16_t *distanceCm, uint8_t print);
void    acq_count_measurements(uint16_t *distanceCm, uint8_t print);
void    burst_measurements(uint16_t *distanceCm, uint16_t numBurst, uint8_t print);


#endif /* INC_GARMINLIDARLITEV3_H_ */
