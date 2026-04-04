# RC Car Mark I

## Overview
This is my master's project for an attempt to make an adaptive cruise controller on an RC car using STM32 microcontrollers. The transmitter will be controlled by a Python GUI with features that include:

- PID gain values input to tune the PID controller.
- Controls for the RC car.
- RC car has accelerometer to measure its velocity, and LIDAR to measure the relative distance for any leading cars.
- Data acquisition measured for both LIDAR and Accelerometer based on the sample time.

## Hardware

### RC Car
- Garmin V3 Lite LIDAR
- LIS3DH Accelerometer
- IBT-4, 50A H-Bridge MOSFET Driver Chip
- NRF24L01 LoRa RF Sensor
- Nucleo H723ZG MCU
- SN74HCT595 8-Bit Shift Registers — controls LEDs using SPI for marking states in the program (serves as a marker to troubleshoot program)

### Transmitter
- NRF24L01 LoRa RF Sensor
- SN74HCT595 8-Bit Shift Registers — controls LEDs using SPI for marking states in the program (serves as a marker to troubleshoot program)
- Hooked to micro-USB to use UART Protocol for Python GUI to communicate with MCU
- Nucleo L432KC MCU

## Software

### STM32CubeIDE
Built with STM32CubeIDE on Debian. Open the workspace and import both projects.

### Python GUI

The GUI communicates with the transmitter MCU over serial (UART). It requires the following Python packages:

| Package | Purpose |
|---------|---------|
| `PyQt5` | GUI framework (widgets, signals, timers) |
| `serial` / `pyserial` | Serial port communication with the MCU |
| `sys`, `os`, `time` | Standard library utilities |

#### Wayland Note
On Wayland, Qt may trigger the warning: *"qt.qpa.wayland: Wayland does not support QWindow::requestActivate()"*. The GUI handles this by silencing the Wayland QPA logging category. To force X11 via XWayland instead, set the environment variable before running:

