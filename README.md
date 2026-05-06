# RC Car Mark I

This is my Masters of Electrical Engineering which is an attempt to make an Adaptive Cruise Control on a RC Car. 

## Project Overview

The purpose of this project will explore the realms electronics, embedded systems, mechanics, control engineeing, software development, sensor practicalites, and data acquisition. The RC Car regarding to the hardware, I wanted to explore control systems in practice including sensor integration need to make the RC Car drive autonomously at its tuned speed, slow down or stop when it detect vehicle/object ahead. Along making the control systems possible a python software is developed for real time data acquisition so that the signal collected can used for the control systems. 

## Engineering Disciplines Involved
- Embedded Systems (STM32H7, STM32L432KC)
- Wireless Communication (NRF24L01 2.4GHz)
- Sensor Integration (LIS3DH IMU, Garmin LIDAR Lite V3)
- Real-Time Data Acquisition & Visualization (Python/PyQt5)
- PCB/Perfboard Hardware Design

## System Architecture
The Architecture setup for the project is shown in the block diagram at a highlevel overview.

![RC Car](/docs/images/blockDiagrams/blockDiagramHighlLevelProject.png)
*Figure 1: High level overview of the project functionality.*

The transmiter board has the stm32 L432KC Nucleo-Board which has 4 colored status LEDs to indicate the events in the program, and NRF24L01 RF module to communicate with the RC Car. The transmitter has a USB connection with computer in order for the Python User Interface to send commands to the transmiter and collect data it has received from the RC Car as shown below.

![RC Car](/docs/images/picturesGeneral/transmitterAndPythonUserInterface.jpg)
*Figure 2: The transmitter connected to the PC with the Python User Interface.*

The RC Car also has the NRF24L01 RF module to communicate with each other based on the commands it has received from the Python User face as shown below.

![RC Car](/docs/images/picturesGeneral/transmitterAndRC_Car.jpg)
*Figure 3: The transmitter and RC Car.*

With the transmitter Micro-USB cable hooked to the computer, the user interface made in Python as shown below connects the transmitter by UART protocol. Once connect the Calibration button opens to calibrate the accelerometer, the sliders are configured based on the direction the car will be going and its speed will be controlled by the slider, and the steering control by moving the dial. When the RC car is either steering or to move forward/backwards the data from the data from the accelerometer and LIDAR is collected to determine the velocity of the car and the data can be exported in a csv to analyze the data.

![RC Car](/docs/images/picturesGeneral/PythonGUI.png)
*Figure 4: The Python User Interface with the calibration window open.*



## Sub-Projects

The entire project consist of three subprojects based on the described System Architecture section. Each of the sub project will provide the ReadMe.md layout with the description high level system, state diagrams, schematic, Hardware/Software used in further details.

| Folder | Description |
|--------|-------------|
| `rc_car_integrated_II/` | STM32H7 RC car firmware — sensors, motor control, wireless TX |
| `RC_Car_Transmitter_L432KC/` | STM32L432KC transmitter firmware — relay between radio and PC |
| `Python_GUI/` | Real-time data logging and control GUI |



## Test Run

Here is a small video attach of the working project (Will add video soon)


*Figure 5: As small test run video.*

## Key Challenges

The RC Car was able to respond to the user interface and received data, however there some challenges that were faced in the project.

- Data Acquisition
    The RC car and transmitter is toggling the NRF24L01 RF module to Listen/Talk mode (Transmit/ Receive Mode) at the fastest as 10ms. As a result it will be receiving data every 20ms based on how it is switching modes. However after the RC Car crashed from a test drive, the socket to put the NRF24L01 RF module is potentially loose and would sometimes cut communication for about a 1s and then communicate again but is able to receive the next data point it has received for a moment. The next plan the is add an enclosure and move the NRF24L01 to the center of the RC Car and would need to be solder and potentially add a larger bypass capacitor to maintain the supply voltage of the RF module.
    Here below shows the data aquisition in real time where there are time gaps for a second and then eventually resume collecting the data. The time gap will impact on transmitting commands to the RC Car, and also impact the velocity estimation as it will be explained in the next section. 
    
![RC Car](/docs/images/picturesGeneral/timeGapIssue.png)
    *Figure 6: The Python User Interface with marking where the NRF24L01 lost communication and reconnected again afterwards.*
    
- Real-time velocity estimation
    The data aquisition of the accelerator was a success, and the user interface storing the acceleration data in buffer. Using the acceleration data, a numerical integration was applied to estimate the velocity at the moment of time. The calculation used for numerically integrating the velocity uses Euler Method of Integration which is derived below.
    
![RC Car](/docs/images/picturesGeneral/EulerIntegrationMethod.png)
    *Figure 7: Euler Integration Technique.*
    
The integration technique was able to calculate the velocity but there arises three challenge
    
        1. The small noise over time is will cause the velocity to drift away from the approximate which is a issue when integrating numerically.
        2. If the RC car is moving but decides to stop, the integration technique does not have an initial condition measured to know if the RC Car has stopped and will show the RC Car traveling at constant speed.
        3. The stationary RC car, is tilted at small angle in which the accelerometer on the x component feels a small pull from Earth gravity. (The Z-axis show the acceleration near 1000mg = 1g = 9.81m/s^2)
    
   An attempt resolve most off three challenges, a calibration feature is added before running the RC car so the influence of Earth's gravity can be filtered out and track basically the change in motion of the RC car. The calibration will measure the acceleration and then get average out to calculate the offset required to add. Below shows the waveform of what the accelerometer measures without calibration vs with calibration for 4.5s.
    
![RC Car](/docs/images/picturesGeneral/NoCalibrationWF.png)
    *Figure 8: The waveform of accelerometer without calibration.*
    
![RC Car](/docs/images/picturesGeneral/CalibrationWF.png)
    *Figure 8: The waveform of accelerometer with calibration.*

By calibrating it will calculate the velocity a little more accurate and drift from integration becomes small difference but still will add up eventual if stays still long enough as shown in the calibration waveform. This alone would not fully solve the challenge more a band-aid solution. Other sensors can implement such a hall effect sensor where the L4133 could be attach to the wheel and a magnet can stick on the wheel to generate a pulse momentarily and based on the time difference between the wheel, the linear velocity can be calculated. Another sensor such as the GPS can potentially track the position precisely. It would be effective to include more sensors to measure more physicals parameter so that more initial conditions about the car can be used to calculate the velocity of the car known as sensor fusion. 

- Non-blocking LIDAR integration to prevent main loop stalls
- Bidirectional NRF24 communication with synchronized TX/RX windows



## Report
See [RC_Car_Report.pdf](RC_Car_Report.pdf) for full technical documentation. (Not editted yet.)
