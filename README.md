# RC Car Mark I

This is my Masters of Electrical Engineering which is an attempt to make an Adaptive Cruise Control on a RC Car. 

## Project Overview
2-3 sentences: what it does, why you built it, what it demonstrates.
The purpose of this project will explore the realms electronics, embeded systems, mechanics, control engineeing, software development, sensor practicalites, and data acquisition. The RC Car regarding to the hardware, I wanted to explore control systems in practice including sensor integration need to make the RC Car drive autonomously at its tuned speed, slow down or stop when it detect vehicle/object ahead. Along making the control systems possible a python software is developed for real time data acquisition so that the signal collected can used for the control systems. 

## Engineering Disciplines Involved
- Embedded Systems (STM32H7, STM32L432KC)
- Wireless Communication (NRF24L01 2.4GHz)
- Sensor Integration (LIS3DH IMU, Garmin LIDAR Lite V3)
- Real-Time Data Acquisition & Visualization (Python/PyQt5)
- PCB/Perfboard Hardware Design

## System Architecture
The Architecture setup for the project is shown in the block diagram at a highlevel overview.
![RC Car](/docs/images/blockDiagrams/blockDiagramHighlLevelProject.png)
The transmiter board has the stm32 L432KC Nucleo-Board which has 4 colored status LEDs to indicate the events in the program, and NRF24L01 LoRa RF module to communicate with the RC Car. The transmitter has a USB connection with computer in order for the Python User Interface to send commands to the transmiter and collect data it has received from the RC Car as shown below.
![RC Car](/docs/images/picturesGeneral/transmitterAndPythonUserInterface.jpg)
The RC Car also has the NRF24L01 LoRa RF module to communicate with each other based on the commands it has received from the Python User face as shown below.
![RC Car](/docs/images/picturesGeneral/transmitterAndRC_Car.jpg)



## Sub-Projects
The entire project consist of three subprojects based on the described System Architecture section. Each of the sub project will provide the ReadMe.md layout with the description high level system, state diagrams, schematic, Hardware/Software used.

| Folder | Description |
|--------|-------------|
| `rc_car_integrated_II/` | STM32H7 RC car firmware — sensors, motor control, wireless TX |
| `RC_Car_Transmitter_L432KC/` | STM32L432KC transmitter firmware — relay between radio and PC |
| `Python_GUI/` | Real-time data logging and control GUI |

## Key Challenges
- Achieving consistent 40ms wireless data sampling under motor RF noise
- Non-blocking LIDAR integration to prevent main loop stalls
- Bidirectional NRF24 communication with synchronized TX/RX windows
- Real-time velocity estimation from accelerometer integration


## Report
See [RC_Car_Report.pdf](RC_Car_Report.pdf) for full technical documentation.
