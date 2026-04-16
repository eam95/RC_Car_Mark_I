# from GarminDialogs import acquireCommandChangeWindow, SensitivityWindow, AcqMeasureSettingsDialog, SemiBurstMeasureSettingsDialog
# Ensure Qt environment variables are set before importing PyQt5/initializing Qt.
# On Wayland some Qt calls trigger the warning:
#   "qt.qpa.wayland: Wayland does not support QWindow::requestActivate()"
# We try a non-invasive approach first: silence the Wayland QPA logging category.
# If you prefer to force X11 (via XWayland), set the environment variable
# FORCE_QPA_XCB=1 outside Python (or before running this script) to enable the xcb platform plugin.
import os
if os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland' or 'WAYLAND_DISPLAY' in os.environ:
    # Do not override user's existing settings; only set defaults if not present.
    # Silence Wayland QPA warning messages (non-invasive).
    # Note: the exact logging rule may vary across Qt versions; this rule disables the
    # "qt.qpa.wayland" warning category. If you'd rather see other Qt logs, unset
    # QT_LOGGING_RULES in your environment.
    os.environ.setdefault('QT_LOGGING_RULES', 'qt.qpa.wayland.warning=false')
    # Optional fallback: force Qt to use the XCB (X11) platform plugin via XWayland.
    # Enable by exporting FORCE_QPA_XCB=1 in your environment before running the script.
    if os.environ.get('FORCE_QPA_XCB') == '1':
        os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')

from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QComboBox, QPushButton, QTextEdit,
                             QSlider, QRadioButton, QButtonGroup)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

import serial
import serial.tools.list_ports
import pyqtgraph as pg
from collections import deque
import time

from RC_Car_SerialThread import SerialReaderThread
from RC_CarMainWindowWidgets import MainWindowWidgetSetup

def formatTwoWordData(data):
    # normalize to bytes
    b = data.encode('utf-8') if isinstance(data, str) else bytes(data)
    # produce exactly 32 bytes of content (padded with NUL)
    twoWordFormat = b[:32].ljust(32, b'\0')
    # Add a \n onlast byte
    twoWordFormat = twoWordFormat[:-1] + b'\n'
    return twoWordFormat

class MainWindow(QMainWindow):

    rx_data_signal = pyqtSignal(str) # Help signal the Rx textbox to update

    def __init__(self):
        super().__init__()
        self.serial_port = None

        self.setWindowTitle("RC Car Controller")
        self.setGeometry(100, 100, 1000, 900)
        # Setup a modular function to setup textbox messages
        MainWindowWidgetSetup.setup_textbox_messages(self)
        # Setup a modular function to setup the UART widgets (baud, com, connect, refresh)
        MainWindowWidgetSetup.setup_uart_widgets(self)
        # Setup a modular function for the pwm setup widgets
        MainWindowWidgetSetup.setup_pwm_widgets(self)

    def append_rx_text(self, text):
        self.RxText_box.append(text)
        self.RxText_box.verticalScrollBar().setValue(
            self.RxText_box.verticalScrollBar().maximum())

    def send_serial_data(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data)
                # print(f"Sent '{data}' to {self.serial_port.port} at {self.serial_port.baudrate} baud.")
                data = data.decode(errors='ignore').replace('\0', '').replace('\n', '').strip()
                self.text_box.append(f"Sent: {data}")
            except Exception as e:
                print(f"Error sending data: {e}")
        else:
            print("Serial port is not open.")

    # The QtThread called from the RC_Car_SerialThead where if it gets a signal a data is received it will print the data
    def on_data_received(self, t, x, ax, ay, az):
        msg = f"t= {t: .2f} s, x= {x: .1f} cm, ax= {ax: .0f} g, ay= {ay: .0f} g, az= {az: .0f} g"
        print(msg)  # console
        self.RxText_box.append(msg)
        self.RxText_box.verticalScrollBar().setValue(
            self.RxText_box.verticalScrollBar().maximum()
        )



    def refresh_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_combo.clear()
        self.com_combo.addItems(ports if ports else ["No ports found"])
        self.text_box.append(f"COM ports refreshed.")

    def connect_to_microcontroller(self):
        baud = int(self.baud_combo.currentText())
        com = self.com_combo.currentText()
        try:
            # self.serial_port.reset_input_buffer()  # Clear old data
            self.serial_port = serial.Serial(com, baud, timeout=0.1)
            self.dir_disabled_rb.setEnabled(True)
            self.dir_forward_rb.setEnabled(True)
            self.dir_backward_rb.setEnabled(True)
            self.text_box.append(f"Connected to {com} at {baud} baud.")

            # start QThread reader
            self.reader_thread = SerialReaderThread(self.serial_port)
            self.reader_thread.data_received.connect(self.on_data_received)
            self.reader_thread.start()

        except Exception as e:
            self.text_box.append(f'Error connecting: {e}')

    def disconnect_com_port(self):
        if self.serial_port and self.serial_port.is_open:
            # stop thread before closing port
            if hasattr(self, 'reader_thread') and self.reader_thread.isRunning():
                self.reader_thread.stop()

            self.serial_port.close()
            self.text_box.append(f"Disconnected from {self.serial_port.port}.")
            self.serial_port = None

            self.pwm_slider.setEnabled(False)  # enabled when connected
            self.dir_disabled_rb.setEnabled(False)
            self.dir_forward_rb.setEnabled(False)
            self.dir_backward_rb.setEnabled(False)
        else:
            self.text_box.append("No COM port is currently connected.")

    def on_direction_change(self, button):
        # Determine which radio is selected and enable/disable slider accordingly
        if self.dir_disabled_rb.isChecked():
            self.current_direction = None
            self.pwm_slider.setEnabled(False)
            # send a zero duty to stop the motor
            if hasattr(self, "serial_port") and self.serial_port and self.serial_port.is_open:
                cmd = f"C,0"  # 'C' for coast/disable
                print(cmd)
                print('Coast the motor (disable)')
                cmd = formatTwoWordData(cmd)
                self.send_serial_data(cmd)
            self.text_box.append("Direction: Disabled (slider off)")
            self.pwm_label.setText("PWM: 0")
            self.pwm_slider.setValue(0)
        else:
            # Forward or Backward selected
            if self.dir_forward_rb.isChecked():
                self.current_direction = 'F'
                self.pwm_slider.setValue(0)
                self.text_box.append("Direction: Forward")
            else:
                self.current_direction = 'R'
                self.pwm_slider.setValue(0)
                self.text_box.append("Direction: Backward")
            # enable slider so user can set duty
            self.pwm_slider.setEnabled(True)
            self.on_pwm_change(0)  # send initial 0% duty

    def on_pwm_change(self, value):
        # update UI immediately, but defer sending
        self._last_pwm_value = value
        self.pwm_label.setText(f"PWM: {value}")
        self.text_box.append(f"Setting pwm to {value}")
        # restart debounce timer so send happens after user stops moving slider
        self.pwm_debounce_timer.start()

    # Add these helper methods to MainWindow
    def on_slider_released(self):
        # send immediately on release (final value)
        if self.pwm_debounce_timer.isActive():
            self.pwm_debounce_timer.stop()
        self.send_debounced_pwm()

    def send_debounced_pwm(self):
        value = getattr(self, "_last_pwm_value", self.pwm_slider.value())
        if hasattr(self, "serial_port") and self.serial_port and self.serial_port.is_open and self.current_direction:
            cmd = f"{self.current_direction},{value}"
            cmd = formatTwoWordData(cmd)
            self.send_serial_data(cmd)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())