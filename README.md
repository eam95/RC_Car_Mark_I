# RC Car Mark I

## Project Overview

This project is a Master of Electrical Engineering capstone that explores the development of an Adaptive Cruise Control system implemented on an RC Car. The project spans multiple engineering disciplines such as electronics, embedded systems, mechanics, control engineering, software development, sensor practicalities, and data acquisition. The RC Car regarding to the hardware, the main heart of the project is to put control engineering into practice including sensor integration and limitation, drive the RC Car autonomously at its tuned speed, slow down or stop when it detects vehicle/object ahead. To place control engineering into practice, a Python user interface is developed for real time data acquisition, in order to extract signals for analysis and used for control systems development.The goal of the project is fully utilize the accelerometer, LIDAR in order to analyze the velocity of the RC Car over time and tune its speed. For the LIDAR in the otherhand, the relative distance is measured between the RC Car and any object ahead in order for the RC Car to slow down or stop for any moving or stationary object.

## Engineering Disciplines Involved
- Embedded Systems (STM32H7, STM32L432KC Microcontrollers)
- Sensor Integration (LIS3DH IMU, Garmin LIDAR Lite V3, NRF24L01 2.4GHz)
- Real-Time Data Acquisition & Visualization (Python/PyQt5)
- PCB/Perfboard Hardware Design

## Installation Requirements and Sub-Projects

The project consists of four sub-projects: the RC Car Firmware, Transmitter Firmware for the RC Car, and the Python user interface for RC Car commands and real time data acquisition as shown in the table below. The subfolder for each project will go into further detail such as the program functionality, hardware requirements and schematic if any, and necessary packages.


| Folder | Description | Software | Version |
|--------|-------------|----------|---------|
| [`rc_car_integrated_II/`](rc_car_integrated_II/) | STM32H723ZG RC car firmware — sensors, motor control, wireless TX | STM32CubeIDE | 1.19 |
| [`RC_Car_Transmitter_L432KC/`](RC_Car_Transmitter_L432KC/) | STM32L432KC transmitter firmware — relay between radio and PC | STM32CubeIDE | 1.19 |
| [`Python_GUI/`](Python_GUI/) | Real-time data logging and control GUI (Linux) | PyCharm 2025 | Python 3.13.5 |
| [`Python_GUI_Windows_Version/`](Python_GUI_Windows_Version/) | Real-time data logging and control GUI (Windows) | PyCharm 2025 | Python 3.11.15 |

## System Architecture
The Architecture setup for the project is shown in the block diagram at a high-level overview.

![RC Car](/docs/images/blockDiagrams/blockDiagramHighlLevelProject.png)
*Figure 1: High-level overview of the project functionality.*

The transmitter board has the stm32 L432KC Nucleo-Board which has 4 colored status LEDs to indicate the events in the program, and NRF24L01 RF module to communicate with the RC Car. The transmitter has a USB connection with computer in order for the Python User Interface to send commands to the transmitter and collect data it has received from the RC Car as shown below.

![RC Car](/docs/images/picturesGeneral/transmitterAndPythonUserInterface.jpg)
*Figure 2: The transmitter connected to the PC with the Python User Interface.*

The RC Car also has the NRF24L01 RF module to communicate with each other based on the commands it has received from the Python user interface as shown below.

![RC Car](/docs/images/picturesGeneral/transmitterAndRC_Car.jpg)
*Figure 3: The transmitter and RC Car.*

With the transmitter Micro-USB cable hooked to the computer, the user interface made in Python as shown below connects the transmitter by UART protocol. Once connected the Calibration button opens to calibrate the accelerometer, the sliders are configured based on the direction the car will be going and its speed will be controlled by the slider, and the steering control by moving the dial. When the RC car is either steering or to move forward/backwards, the data from the accelerometer and LIDAR is collected to determine the velocity of the car and the data can be exported in a csv to analyze the data.

![RC Car](/docs/images/picturesGeneral/PythonGUI.png)
*Figure 4: The Python User Interface with the calibration window open.*



## Test Run

There is a two small ~5mins video of the RC Car being able to move and collect data in real time (close to fullly collecting data). The second video shows the calibration feature.


https://www.youtube.com/watch?v=ox59gKyVjFU&t=96s

*Figure 5: As small test run video.*

https://www.youtube.com/watch?v=ydO1_pEh5iw&t=91s


*Figure 6: Calibration Feature.*


## Key Challenges

The RC Car was able to respond to the user interface and received data, however there some challenges that were faced in the project.

- **Data Acquisition**

    The RC car and transmitter is toggling the NRF24L01 RF module to Listen/Talk 
    mode (Transmit/ Receive Mode) as fast as 10ms. As a result it will be 
    receiving data every 20ms based on how it is switching modes. However after 
    the RC Car crashed from a test drive, the socket to put the NRF24L01 RF module 
    is potentially loose and would sometimes cut communication for about a 1s and 
    then communicate again but is able to receive the next data point it has 
    received for a moment. The next plan is to add an enclosure and move the 
    NRF24L01 to the center of the RC Car and would need to be soldered and 
    potentially add a larger bypass capacitor to maintain the supply voltage of 
    the RF module.
    
    Here below shows the data acquisition in real time where there are time gaps 
    for a second and then eventually resume collecting the data. The time gap will 
    impact on transmitting commands to the RC Car, and also impact the velocity 
    estimation as it will be explained in the next section.

    ![RC Car](/docs/images/picturesGeneral/timeGapIssue.png)

    *Figure 7: The Python User Interface with marking where the NRF24L01 lost 
    communication and reconnected again afterwards.*

- **Real-time Velocity Estimation**

    The data acquisition of the accelerometer was a success, and the user interface stores the acceleration data in buffer. Using the acceleration data, a numerical integration was applied to estimate the velocity at the moment of time. The calculation used for numerically integrating the velocity uses Euler 
    Method of Integration which is derived below.

    ![RC Car](/docs/images/picturesGeneral/EulerIntegrationMethod.png)

    *Figure 8: Euler Integration Technique.*

    The integration technique was able to calculate the velocity but 
    three challenges arise:

    1. Small noise over time will cause the velocity to drift away from the approximate which is a issue when integrating numerically.
    2. If the RC car is moving but decides to stop, the integration technique does not have an initial condition measured to know if the RC Car has stopped and will show the RC Car traveling at constant speed.
    3. The stationary RC car, is tilted at small angle in which the accelerometer on the x component feels a small pull from Earth gravity. (The Z-axis show the acceleration near 1000mg = 1g = 9.81m/s^2)

    An attempt to resolve most of the three challenges, a calibration feature is added before running the RC car so the influence of Earth's gravity can be filtered out and track basically the change in motion of the RC car. The calibration will measure the acceleration and then get average out to calculate the offset required to add. Below shows the waveform of what the accelerometer measures without calibration vs with calibration for 4.5s.

    ![RC Car](/docs/images/picturesGeneral/NoCalibrationWF.png)

    *Figure 9: The waveform of accelerometer without calibration.*

    ![RC Car](/docs/images/picturesGeneral/CalibrationWF.png)

    *Figure 10: The waveform of accelerometer with calibration.*

    By calibrating it will calculate the velocity a little more accurate and drift from integration becomes small difference but still will add up eventual if stays still long enough as shown in the calibration waveform. This alone would not fully solve the challenge more a band-aid solution. Other sensors can 
    implement such a hall effect sensor where the A1133 could be attach to the wheel and a magnet can stick on the wheel to generate a pulse momentarily and based on the time difference between the wheel, the linear velocity can be calculated. Another sensor such as the GPS can potentially track the position precisely. It would be effective to include more sensors to measure more 
    physical parameters so that more initial conditions about the car can be used to calculate the velocity of the car known as sensor fusion.

## Future Works
With the success on most of the data acquisition, and basic controls of the RC car, this project can be improvised to become an adaptive cruise which was the project's objective. Although no PID control was implemented yet, adding more sensors to obtain more measurable initial conditions can help obtain more accurate measurements.With sensor fusion becoming a potential solution to have accurate waveforms especially calculated waveforms, is have a clean waveforms. There are two algorithms that comes into mind on filter most of the noise. One can be the Savitzky-Golay algorithm which would grab a window number of points and fit into cubic polynomial as a method similar to a moving averager but much smoother and require less points compare to a moving averager to smoothen the curve. Another but popular method to clean noisy signal is the Kalman Filter, where sensor fusion plays a huge role. The point of Kalman Filter is that accelerometer is still used but other sensors can be incorporated such as Hall Effect sensor to measure RPM of the vehicle and eventually calculate the velocity of the RC Car. The calculated velocity from the Hall effect is the observed speed and would be less concern measurements being drift compare on the attempt on the accelerometer where integration ends up drifting the measurements. The accelerometer on the otherhand will be the predictor where it can still integrate to get the velocity but won't know the initial condition of the RC Car unless another sensor is incorporated to correct the predicted velocity with the observed velocity. During testing of the RC Car where it was driven at a constant speed (Ignore the noise) and all of sudden the RC Car stopped. The accelerometer purpose is detect a change of motion where but as soon as the car is at constant speed or it completely stop. The accelerometer reading does not know if the car is at constant speed or it stop. That is where additional sensors inform the RC Car its observed state. Further detail on the mathematical foundation can be found (https://kalmanfilter.net/stateextrap.html).

## Report
See [RC_Car_Report.pdf](RC_Car_Report.pdf) for full technical documentation. (Not edited yet.)
