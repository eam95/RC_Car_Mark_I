/*
 * ledAdpater.h
 *
 *  Created on: Apr 7, 2026
 *      Author: mongoose
 */

#ifndef INC_LEDADAPTER_H_
#define INC_LEDADAPTER_H_

/* LED SPI Control */
#define OFF_LED_EXT            0x00
#define LIGHT_GREEN_LED_EXT    0x01
#define WHITE_LED_EXT          0x02
#define PINK_LED_EXT           0x04
#define BLUE_LED_EXT           0x08
#define GREEN_LED_EXT          0x10
#define YELLOW_LED_EXT         0x20
#define ORANGE_LED_EXT         0x40
#define RED_LED_EXT            0x80

void shift_register_send(uint8_t data);

#endif /* INC_LEDADAPTER_H_ */
