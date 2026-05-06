# RC Car The Nucleo-H723ZG board

## Overview
The RC Car will drive itself automatically by a PID controller and hopefully could be an adaptive cruise controller soon as it detects a stationary object or another car is ahead. The following sensor are incorporated to the RC car:

- NRF24L01 RF Sensor using the SPI protocol
- External SN74HCT595 8-Bit Shift Registers Adapter, controls LEDs using SPI protocol for marking states in the program (serves as a marker to troubleshoot program, and not used yet)
- Garmin Lite V3 LIDAR that can read distance up to 40m.
- LIS3DH accelerometer as an attempt to calculate its speed.
- IBT-4, 50A H-Bridge MOSFET Driver Chip (PWM frequency is programmed at 4kHz)
- FOD8001 Logic Optocoupler (Isolate the MCU from the power circuit of the motor)
- TMH1205S Traco Power Isolated DC-DC converter (Power the MCU).
- HiLetgo DC/DC step down converter 75W
- LM317 Adjustable Voltage Regulator
- Rapthor Rechargeable 12V 5200mAh Lithium ion Battery Pack Model BP007
- Servo motor (PWM frequency is programmed at 50Hz but pulsed within 1-2ms to control the steering)
- DC Motor

With all the modules and components used the data read from the sensor is packaged into a 32byte format and then transmitted but to the transmitter.

## Schematic

![RC Car](../docs/schematics/RC_Car_Schematic.png)

The schematic of the RC Car where it is powered by a 12V rechargable battery, but the schematic is divided by two sections. Note inside the yellow box is the Nucleo Board H723ZG connected to all the sensors but all the ground are digital ground, whereas inside the green box has all the grounds are power grounds which has the power related circuit. That is due to using a TMH1205S Traco Power Isolated DC-DC converter which powers the MCU but the ground is isolated and vice versa with the optocouplers to transmit the signal to control the servo motor, and DC motor.

## Functionalities
The RC car is toggling the NRF24L01 from listen/talking mode (Rx/Tx mode) every 10ms (using periodic timer interrupt to toggle comm mode) so it can receive commands and data in the Bidirectional Communication mode. The python user interface, sends the commands to the RC car to stop or go forward/backward based on PWM value given. Once the RC Car recognizes it receive a command to move forward/backward it starts measure the distance from the LIDAR, and accelerations from the accelerometer with timestamp it is measured when it is Rx mode. Along with the moving the RC Car the servo motor is also controlled a PWM with a pulse within 1-2ms at 50Hz. As mentioned in the front page of the repo, the accelerometer is calibrated by sending a "CAL" command where it can transmit the acceleration data. Once the enough acceleration data is collected it is posted process and the average offset value along with the std deviation is calculate in order for the user interface to offset the raw measurement, form the RC Car. 

    
### STM32CubeIDE
Built with STM32CubeIDE on Debian. Open the workspace and import both projects.
- Note: change the gbd on the Debug launch file if Debian is used. The project won't debug if it can't find the correct gbd. Look a at line 65 and change the gbd from arm-none-eabi-gdb to gdb-multiarch. Make sure to install multiarch gdb.




