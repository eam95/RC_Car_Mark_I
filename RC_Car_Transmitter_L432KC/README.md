# Transmitter The Nucleo-L432KC board

## Overview
The Transmitter is responsible to transmit and collect data from the RC car that it has acquired over a given sample time. The module listed below are what is build as transmitter:

- NRF24L01 LoRa RF Sensor using the SPI protocol
- SN74HCT595 8-Bit Shift Registers — controls LEDs using SPI protocol for marking states in the program (serves as a marker to troubleshoot program)
- Hooked to micro-USB to use UART Protocol for Python GUI to communicate with MCU
    - The baud rate for the board to perform UART communication is 115200 bits/s.

## Schematic

![RC Car](../docs/schematics/TransmitterSchematic.png)

The schematic of the transmitter is simpler than the RC Car where it just has the UART protocol set up by using a Micro-USB cable to communicate with transmitter. The NRF24L01 will listen/talk to the RC Car based on the commands it receive or it will unpackage the data it received and transmit back to the python user interface. IN order to physically check if the transmitter is operation a shift register with 4 LEDs are used to indicate whether it toggling between listen/talk mode, a Red LED to indicate it is receiving data, and finally a green LED to indicate that transmitter has received a command for the user interface. 

## Functionalities
The Transmitter is designed to waits a UART interrupt to send a command to the RC Car to move forward and backwards for now. Once it is one of these movement the RC car will be transmit the data back to the transmitter to perform data logging. The Transmitter will be toggling the NRF24L01 from listen/talking mode (Rx/Tx mode) every 10ms (using periodic timer interrupt to toggle comm mode) so it can receive commands and data in the Bidirectional Communication mode. 

### STM32CubeIDE
Built with STM32CubeIDE on Debian. Open the workspace and import both projects.
- Note: change the gbd on the Debug launch file if Debian is used. The project won't debug if it can't find the correct gbd. Look a at line 65 and change the gbd from arm-none-eabi-gdb to gdb-multiarch. Make sure to install multiarch gdb.




