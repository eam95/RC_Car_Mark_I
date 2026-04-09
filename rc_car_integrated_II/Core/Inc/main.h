/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32h7xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define ce_Pin GPIO_PIN_6
#define ce_GPIO_Port GPIOF
#define csn_Pin GPIO_PIN_7
#define csn_GPIO_Port GPIOF
#define LED_GREEN_Pin GPIO_PIN_0
#define LED_GREEN_GPIO_Port GPIOB
#define LED_RED_Pin GPIO_PIN_14
#define LED_RED_GPIO_Port GPIOB
#define STLK_VCP_RX_Pin GPIO_PIN_8
#define STLK_VCP_RX_GPIO_Port GPIOD
#define STLK_VCP_TX_Pin GPIO_PIN_9
#define STLK_VCP_TX_GPIO_Port GPIOD
#define CS_LED_Pin GPIO_PIN_6
#define CS_LED_GPIO_Port GPIOC
#define SWDIO_Pin GPIO_PIN_13
#define SWDIO_GPIO_Port GPIOA
#define SWCLK_Pin GPIO_PIN_14
#define SWCLK_GPIO_Port GPIOA
#define IQR_RF_Pin GPIO_PIN_0
#define IQR_RF_GPIO_Port GPIOE
#define LED_YELLOW_Pin GPIO_PIN_1
#define LED_YELLOW_GPIO_Port GPIOE

/* USER CODE BEGIN Private defines */
#define UART_DMA_RX_SIZE 32
#define PLD_S 32
typedef struct
{
	// Disregarding the cmd, all the variables byte size should add up to 18-20bytes
		uint8_t cmd[PLD_S]; // Will grab all the structure variables compress to string and transmit through NRF24L01
		int32_t a_x; // Store the acceleration in x-axis
	    int32_t a_y; // Store the acceleration in y-axis
	    int32_t a_z; // Store the acceleration in z-axis
	    uint16_t distance_cm; // Store the distance measurement in centimeters
	    char stationaryFlag;  // This is Flag to indicate back to the transmitter whether there is a stationary object when the car is accelerating.
	    uint32_t timestamp; // in milliseconds
	    uint8_t transmitFlag; // This flag is used to indicate whether the data is ready to be transmitted, which will be set after getting the sensor data and will trigger the transmission in the main loop when in TX_STATE.
} DataToTransmit;
extern DataToTransmit Transmit; // Added the transmit structure so I can access it in the other files.

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
