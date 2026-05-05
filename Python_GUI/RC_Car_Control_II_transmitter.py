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
                             QSlider, QRadioButton, QButtonGroup, QFileDialog, QMessageBox, QDial)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

import serial
import serial.tools.list_ports
import pyqtgraph as pg
from collections import deque
import time
import pandas as pd
import os

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
        self.is_calibration_active = False # Flag when it is in calibration
        self.buf_t_cal = []
        self.buf_ax_cal = []
        self.buf_ay_cal = []
        self.buf_az_cal = []
        self.calibration_offsets = None

        # Show the directory textbox at the top
        self.output_directory = os.path.dirname(os.path.abspath(__file__))
        MainWindowWidgetSetup.setup_directory_textbox(self, self.output_directory)

        self.setWindowTitle("RC Car Controller")
        self.setGeometry(100, 100, 1000, 900)
        # Setup a modular function to setup textbox messages
        MainWindowWidgetSetup.setup_textbox_messages(self)
        # Setup a modular function to setup the UART widgets (baud, com, connect, refresh)
        MainWindowWidgetSetup.setup_uart_widgets(self)
        # Setup clear buffer button to clear plot
        MainWindowWidgetSetup.setup_clear_buffer_button(self)
        # Setup a modular function for the pwm setup widgets
        MainWindowWidgetSetup.setup_pwm_widgets(self)
        # Setup modularized plot setup
        MainWindowWidgetSetup.setup_plot_widgets(self)

        # Setup the accelerometer calibration to offset the accelerometer readings
        MainWindowWidgetSetup.setup_calibration_button(self)




    def select_output_directory(self):
        from PyQt5.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_directory)
        if dir_path:
            self.output_directory = dir_path
            self.directory_textbox.setText(dir_path)

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
        """Handle normal 5-value data - but skip if in calibration mode."""

        if self.is_calibration_active:
            return
        # ── Apply calibration offsets if available ──
        if self.calibration_offsets is not None:
            ax += self.calibration_offsets["ax_offset_mg"]
            ay += self.calibration_offsets["ay_offset_mg"]
            az += self.calibration_offsets["az_offset_mg"]

        msg = f"t= {t: .3f} s, x= {x: .1f} cm, ax= {ax / 1000: .3f} g, ay= {ay / 1000: .3f} g, az= {az / 1000: .3f} g, pwm= {self._last_pwm_value}"
        print(msg)  # console
        self.RxText_box.append(msg)
        self.RxText_box.verticalScrollBar().setValue(self.RxText_box.verticalScrollBar().maximum())

        # Push into rolling buffers
        self.buf_t.append(t)
        self.buf_x.append(x)
        self.buf_ax.append(ax)
        self.buf_ay.append(ay)
        self.buf_az.append(az)
        self.buf_pwm.append(self._last_pwm_value)  # snapshot PWM at this sample

        # Integrate acceleration (mg → m/s²: × 0.001 × 9.81) → velocity
        if self.prev_t is not None:
            dt = t - self.prev_t
            if dt > 0:
                scale = 0.001 * 9.81  # mg → m/s²
                self.curr_vx += ax * scale * dt
                self.curr_vy += ay * scale * dt
                self.curr_vz += az * scale * dt
        self.prev_t = t

        self.buf_vx.append(self.curr_vx)
        self.buf_vy.append(self.curr_vy)
        self.buf_vz.append(self.curr_vz)

        # Only plot once we have data
        if len(self.buf_t) < 2:
            return

        # Refresh curves
        t_list = list(self.buf_t)
        self.curve_x.setData(t_list, list(self.buf_x))
        self.curve_ax.setData(t_list, list(self.buf_ax))
        self.curve_ay.setData(t_list, list(self.buf_ay))
        self.curve_az.setData(t_list, list(self.buf_az))

        self.curve_vx.setData(t_list, list(self.buf_vx))
        self.curve_vy.setData(t_list, list(self.buf_vy))
        self.curve_vz.setData(t_list, list(self.buf_vz))

    def on_calibration_data_received(self, t, ax, ay, az):
        """Handle calibration data separately - send to cal window, not plots."""
        msg = f"t= {t: .3f} s, ax= {ax: .0f} mg, ay= {ay: .0f} mg, az= {az: .0f} mg"

        # Only process if we're actually in calibration mode
        if self.is_calibration_active:
            print(f"[CAL] {msg}")


            # If calibration window is open, send data there
            if hasattr(self, '_cal_window') and self._cal_window is not None:
                self._cal_window.cal_log.append(msg)
                # Push csampled calibration data into buffers so the average is calculated
                self.buf_t_cal.append(t)
                self.buf_ax_cal.append(ax)
                self.buf_ay_cal.append(ay)
                self.buf_az_cal.append(az)
                # Auto-scroll
                self._cal_window.cal_log.verticalScrollBar().setValue(
                    self._cal_window.cal_log.verticalScrollBar().maximum())
        else:
            # Log unexpected calibration data when not in calibration mode
            print(f"[WARNING] Received calibration data while not in calibration mode: {msg}")
            self.text_box.append(f"Unexpected cal data: {msg}")

    def reset_calibration_buffers(self):
        self.buf_t_cal.clear()
        self.buf_ax_cal.clear()
        self.buf_ay_cal.clear()
        self.buf_az_cal.clear()

    def compute_calibration_average(self, min_samples=20):
        n = len(self.buf_ax_cal)
        if n < min_samples:
            return None

        ax_avg = sum(self.buf_ax_cal) / n
        ay_avg = sum(self.buf_ay_cal) / n
        az_avg = sum(self.buf_az_cal) / n

        ax_std = (sum((v - ax_avg) ** 2 for v in self.buf_ax_cal) / n) ** 0.5
        ay_std = (sum((v - ay_avg) ** 2 for v in self.buf_ay_cal) / n) ** 0.5
        az_std = (sum((v - az_avg) ** 2 for v in self.buf_az_cal) / n) ** 0.5

        # % error = (std / |avg|) * 100  — guard against zero-mean axes
        ax_pct = (ax_std / abs(ax_avg) * 100) if ax_avg != 0 else float('inf')
        ay_pct = (ay_std / abs(ay_avg) * 100) if ay_avg != 0 else float('inf')
        az_pct = (az_std / abs(az_avg) * 100) if az_avg != 0 else float('inf')

        # Typical stationary target in mg
        offsets = {
            "ax_offset_mg": -ax_avg,
            "ay_offset_mg": -ay_avg,
            "az_offset_mg":  -az_avg
        }

        self.calibration_offsets = offsets
        return {
            "n": n,
            "ax_avg": ax_avg, "ay_avg": ay_avg, "az_avg": az_avg,
            "ax_std": ax_std, "ay_std": ay_std, "az_std": az_std,
            "ax_pct": ax_pct, "ay_pct": ay_pct, "az_pct": az_pct,
            **offsets,
        }

    def send_clear_buffer(self):
        # Clear the data in the list (buffer so that the plot does grab previous data
        self.buf_t.clear()
        self.buf_x.clear()
        self.buf_ax.clear()
        self.buf_ay.clear()
        self.buf_az.clear()
        self.buf_vx.clear()
        self.buf_vy.clear()
        self.buf_vz.clear()
        self.buf_pwm.clear()

        # Reset velocity integration initial conditions
        self.prev_t  = None
        self.curr_vx = 0.0
        self.curr_vy = 0.0
        self.curr_vz = 0.0

        # Clear the plot with the empty buffer
        self.curve_x.setData([])
        self.curve_ax.setData([])
        self.curve_ay.setData([])
        self.curve_az.setData([])
        self.curve_vx.setData([])
        self.curve_vy.setData([])
        self.curve_vz.setData([])

        # clear output data from the RxText_box
        self.RxText_box.clear()


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
            # Connect calibration data signal (will be routed when cal window is open)
            self.reader_thread.calibration_data_received.connect(self.on_calibration_data_received)
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

            # clear buffer data and plot.
            # self.send_clear_buffer()

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

    def on_steering_change(self, value):
        self._last_steering_value = value
        self.steering_label.setText(f"Steering: {value}")
        self.steering_debounce_timer.start()

    def on_steering_released(self):
        if self.steering_debounce_timer.isActive():
            self.steering_debounce_timer.stop()
        self.send_debounced_steering()

    def send_debounced_steering(self):
        value = getattr(self, "_last_steering_value", self.steering_dial.value())
        if hasattr(self, "serial_port") and self.serial_port and self.serial_port.is_open:
            inverted_value = 150 - value  # flip: 50↔100, center 75 stays 75
            cmd = f"S,{inverted_value}"
            cmd = formatTwoWordData(cmd)
            self.send_serial_data(cmd)

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

    def export_csv(self):
        # Suggest a default filename
        default_path = os.path.join(self.output_directory, "rc_car_data.csv")
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Data to CSV", default_path, "CSV Files (*.csv)")
        if not file_path:
            return
        try:
            df = pd.DataFrame({
                "Time (s)": list(self.buf_t),
                "Distance (cm)": list(self.buf_x),
                "ax (mg)": list(self.buf_ax),
                "ay (mg)": list(self.buf_ay),
                "az (mg)": list(self.buf_az),
                "vx (m/s)": list(self.buf_vx),
                "vy (m/s)": list(self.buf_vy),
                "vz (m/s)": list(self.buf_vz),
                "PWM": list(self.buf_pwm),
            })
            df.to_csv(file_path, index=False)
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export data: {e}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())