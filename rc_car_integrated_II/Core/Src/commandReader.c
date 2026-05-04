/*
 * commandReader.c
 *
 *  Created on: Dec 2, 2025
 *      Author: erick
 *      The functions in this file parse commands and values from a UART received buffer.
 */
#include "delay.h"
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "GarminLidarLiteV3.h"
#include "main.h"
#include "delay.h"

void parse_uart_command(char *uart_rx_buf, char *command_out, uint8_t *indexPointer)
{
    uint8_t i = 0;
    while (uart_rx_buf[i] != ',' && uart_rx_buf[i] != '\0' && i < 32)
    {
        command_out[i] = uart_rx_buf[i];
        i++;
    }
    command_out[i] = '\0'; // null terminate
    indexPointer[0] = i;
}


void parse_uart_value(char *uart_rx_buf, char *value_out, uint8_t *indexPointer)
{
    uint8_t i = indexPointer[0] + 1;
    uint8_t j = 0;
    while (uart_rx_buf[i] != ',' && uart_rx_buf[i] != '\0' && i < 32 && j < 32)
    {
        value_out[j] = uart_rx_buf[i];
        i++;
        j++;
    }
    value_out[j] = '\0'; // null terminate
    indexPointer[0] = i;
}
