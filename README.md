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

The RC Car was able to respond to the user interface and receive data, however 
there were some challenges faced during the project.

- **Data Acquisition**

    The RC Car and transmitter toggle the NRF24L01 RF module between Listen/Talk 
    mode (Receive/Transmit) at 10ms intervals, receiving data every 20ms. After 
    the RC Car crashed during a test drive, the NRF24L01 socket became loose and 
    would occasionally cut communication for ~1s before resuming. The next plan 
    is to add an enclosure, move the NRF24L01 to the center of the RC Car, solder 
    it directly to the board, and add a larger bypass capacitor to maintain stable 
    supply voltage to the RF module.

    The figure below shows the data acquisition in real time where time gaps of 
    approximately one second appear before data collection resumes. These gaps 
    impact command transmission to the RC Car and also affect velocity estimation 
    as described in the next section.

    ![Time Gap Issue](/docs/images/picturesGeneral/timeGapIssue.png)

    *Figure 6: Python GUI showing time gaps where the NRF24L01 lost communication 
    and reconnected.*

- **Real-Time Velocity Estimation**

    The accelerometer data acquisition was successful and the GUI stores the 
    acceleration data in a rolling buffer. Using this data, numerical integration 
    is applied to estimate velocity at each point in time. The Euler method of 
    integration is used, derived as shown below.

    ![Euler Integration](/docs/images/picturesGeneral/EulerIntegrationMethod.png)

    *Figure 7: Euler integration technique used for velocity estimation.*

    This technique was able to estimate velocity, however three challenges arise:

    1. Small noise accumulates over time causing the velocity estimate to drift 
       away from the true value — a known limitation of numerical integration.
    2. When the RC Car stops moving, the integrator has no way to detect the 
       stop condition and continues showing a constant velocity instead of 
       returning to zero.
    3. The stationary RC Car sits at a slight angle, causing the accelerometer 
       X-axis to sense a small component of Earth's gravity. (The Z-axis 
       correctly reads ~1000mg = 1g = 9.81 m/s².)

    To partially address all three challenges, a calibration feature was added. 
    Before running the RC Car, the user collects stationary accelerometer samples 
    which are averaged to compute an offset on each axis. Subtracting this offset 
    filters out the gravitational bias and tracks only changes in motion. The 
    figures below compare the accelerometer waveform without and with calibration 
    over 4.5 seconds.

![No Calibration](/docs/images/picturesGeneral/NoCalibrationWF.png)

*Figure 8: Accelerometer waveform without calibration.*

![With Calibration](/docs/images/picturesGeneral/CalibrationWF.png)

*Figure 9: Accelerometer waveform with calibration applied.*

Calibration improves velocity accuracy and reduces drift noticeably, but it is ultimately a partial solution — drift still accumulates if the car remains
stationary long enough. A more complete solution would involve additional 
sensors such as:
    - A **Hall effect sensor** (e.g. A1133) mounted near the wheel with a magnet 
      to generate pulses — the time between pulses gives precise linear velocity.
    - A **GPS module** for absolute position tracking.

    Combining multiple sensor sources to compute a more accurate state estimate 
    is known as **sensor fusion** and would be the next step for improving 
    velocity estimation reliability.

- **Non-Blocking LIDAR Integration**

    The Garmin LIDAR Lite V3 acquisition can block the main loop when the target 
    is near maximum range or the I2C bus stalls, causing data gaps of up to 1.4s. 
    The solution is a non-blocking pipelined measurement that triggers acquisition 
    at the end of one cycle and reads the result at the start of the next, so the 
    main loop is never held waiting.

- **Bidirectional NRF24 Communication**

    Synchronizing TX/RX windows between two independent MCU clocks causes packet 
    loss when windows misalign. This was addressed by making the transmitter 
    RX-dominant, only briefly switching to TX mode when a command from the GUI 
    is pending.



## Report
See [RC_Car_Report.pdf](RC_Car_Report.pdf) for full technical documentation. (Not editted yet.)
