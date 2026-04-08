# Transmitter The Nucleo-L432KC board

## Overview
The Transmitter is responsible to transmit and collect data from the RC car that it has acquired over a given sample time. The module listed below are what is build as transmitter:

- NRF24L01 LoRa RF Sensor using the SPI protocol
- SN74HCT595 8-Bit Shift Registers — controls LEDs using SPI protocol for marking states in the program (serves as a marker to troubleshoot program)
- Hooked to micro-USB to use UART Protocol for Python GUI to communicate with MCU
    - The baud rate for the board to perform UART communication is 115200 bits/s.

## Functionalities
The Transmitter is designed to waits a UART interrupt to send a command to the RC Car to move forward and backwards for now. Once it is one of these movement the RC car will be transmit the data back to the transmitter to perform data logging. The Transmitter will be toggling the NRF24L01 from listen/talking mode (Rx/Tx mode) every 10ms (using periodic timer interrupt to toggle comm mode) so it can receive commands and data in the Bidirectional Communication mode. 
 - As of 4/7/26
    - There is Bidirectional Communication issue where when the car is forward/backward mode it will receive data for about 3.3s-3.5s and then stop acquiring data for a second.
    - It still collects data again and repeat the same pattern.
    - Using the SPI setup to signal the external LEDs to indicate which part of the program it is at and check the timing through the Logic Analyzer (I have commmited the waveforms on the doc folder.)
    - Yellow LED indicates the stage where it is in tranmitt mode.
    - Blue LED indicates the stage where it is in receive mode.
    - Red LED indicates the stage where it is perform data acquisition when the data was successfully received from the RC car.
    - Green LED indicates that UART interrupt occured, where the MCU has received a command from the computer.

### STM32CubeIDE
Built with STM32CubeIDE on Debian. Open the workspace and import both projects.
- Note: change the gbd on the Debug launch file if Debian is used. The project won't debug if it can't find the correct gbd. Look a at line 65 and change the gbd from arm-none-eabi-gdb to gdb-multiarch. Make sure to install multiarch gdb.




