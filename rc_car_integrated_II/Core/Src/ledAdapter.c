/*
 * ledAdapter.c
 *
 *  Created on: Apr 7, 2026
 *      Author: mongoose
 */

#include "stm32h7xx_hal.h"
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "GarminLidarLiteV3.h"
#include "main.h"
#include "delay.h"
#include "ledAdapter.h"

extern SPI_HandleTypeDef hspi1;

void shift_register_send(uint8_t data)
{
	HAL_GPIO_WritePin(CS_LED_GPIO_Port, CS_LED_Pin, GPIO_PIN_RESET);
	HAL_SPI_Transmit(&hspi1, &data, 1, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(CS_LED_GPIO_Port, CS_LED_Pin, GPIO_PIN_SET);
}
