# RC Car The Nucleo-H723ZG board

## Overview
The RC Car will drive itself automatically by a PID controller and hopefully could be an adaptive cruise controller soon as it detects a stationary object or another car is ahead. The following sensor are incorporated to the RC car:

- NRF24L01 LoRa RF Sensor using the SPI protocol
- External SN74HCT595 8-Bit Shift Registers Adapter — controls LEDs using SPI protocol for marking states in the program (serves as a marker to troubleshoot program)
- Garmin Lite V3 LIDAR that can read distance up to 40m.
- LIS3DH accelerometer as an attempt to calculate its speed.
- IBT-4, 50A H-Bridge MOSFET Driver Chip
- FOD8001 Logic Optocoupler (Isolate the MCU from the power circuit of the motor)
- TMH1205S Traco Power Isolated DC-DC converter (Power the MCU).


## Functionalities
The RC car is toggling the NRF24L01 from listen/talking mode (Rx/Tx mode) every 10ms (using periodic timer interrupt to toggle comm mode) so it can receive commands and data in the Bidirectional Communication mode. The python GUI, sends the commands to the RC car to stop or go forward/backward based on PWM value given. Once the RC Car recognizes it receive a command to move forward/backward it starts measure the distance from the LIDAR, and accelerations from the accelerometer with timestamp it is measured when it is Rx mode. 
 - As of 4/8/26
    - There is Bidirectional Communication issue from the transmitter, when it is forward/backward mode it will receive data for about 3.3s-3.5s and then stop acquiring data for a second.
    - It still collects data again and repeat the same pattern.
    - Need to check the with the logic analyzer, to verify if the RC car is actually transmitting data, when Red on board LED is toggling.
    - Yellow on board LED indicates the stage where it is in Receive mode.
    - Green on board LED indicates the stage where it is in Transmitt mode.
    - Once it Receives a command to stop the car it will quit measuring.
    - To verify the RC car sensors are actually measuring the UART compability is added so it be easier to debug.
        - Baud rate for board is 115200 bits/s

### STM32CubeIDE
Built with STM32CubeIDE on Debian. Open the workspace and import both projects.
- Note: change the gbd on the Debug launch file if Debian is used. The project won't debug if it can't find the correct gbd. Look a at line 65 and change the gbd from arm-none-eabi-gdb to gdb-multiarch. Make sure to install multiarch gdb.




