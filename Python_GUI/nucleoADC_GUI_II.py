import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QWidget, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
import serial
import time
import pandas as pd
import serial.tools.list_ports

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.ticker import AutoLocator, AutoMinorLocator


class SerialReaderThread(QThread):
    data_point = pyqtSignal(float, float)  # time, adc_value
    finished = pyqtSignal(list, list)      # times, adc_values

    def __init__(self, serial_conn, samples):
        super().__init__()
        self.serial_conn = serial_conn
        self.samples = samples
        self._running = True

    def run(self):
        count = 0
        adc_values = []
        times = []
        while count < self.samples and self._running:
            line = self.serial_conn.readline().decode().strip()
            if line:
                parts = line.split(',')
                val = float(parts[0])
                t = float(parts[1])
                adc_val = val/(2**16)*3.3
                time_val = t/1000
                adc_values.append(adc_val)
                times.append(time_val)
                self.data_point.emit(time_val, adc_val)
                count += 1
            else:
                time.sleep(0.001)
        self.finished.emit(times, adc_values)

    def stop(self):
        self._running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_conn = None
        self.setWindowTitle("Microcontroller Connection")
        self.setGeometry(100, 100, 1000, 1000)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.baud_label = QLabel("Select Baud Rate:", central_widget)
        self.baud_label.setGeometry(20, 20, 120, 30)

        self.baud_combo = QComboBox(central_widget)
        self.baud_combo.setGeometry(150, 20, 150, 30)
        self.baud_combo.addItems([
            "9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"
        ])

        self.com_label = QLabel("Select COM Port:", central_widget)
        self.com_label.setGeometry(20, 70, 120, 30)

        self.com_combo = QComboBox(central_widget)
        self.com_combo.setGeometry(150, 70, 150, 30)
        self.refresh_com_ports()

        self.refresh_btn = QPushButton("Refresh", central_widget)
        self.refresh_btn.setGeometry(320, 70, 120, 30)
        self.refresh_btn.clicked.connect(self.refresh_com_ports)

        self.connect_btn = QPushButton("Connect", central_widget)
        self.connect_btn.setGeometry(100, 130, 120, 40)
        self.connect_btn.clicked.connect(self.connect_to_microcontroller)

        self.disconnect_btn = QPushButton("Disconnect", central_widget)
        self.disconnect_btn.setGeometry(250, 130, 120, 40)
        self.disconnect_btn.clicked.connect(self.disconnect_from_microcontroller)

        self.toggle_green_btn = QPushButton("STOP", central_widget)
        self.toggle_green_btn.setGeometry(100, 200, 120, 40)
        self.toggle_green_btn.clicked.connect(self.stop_sampling)
        self.toggle_green_btn.setEnabled(False)

        self.toggle_red_btn = QPushButton("SAMPLE", central_widget)
        self.toggle_red_btn.setGeometry(100, 250, 120, 40)
        self.toggle_red_btn.clicked.connect(self.start_sampling)
        self.toggle_red_btn.setEnabled(False)

        self.canvas = FigureCanvas(Figure())
        self.canvas.setParent(central_widget)
        self.canvas.setGeometry(20, 400, 800, 400)  # Place below buttons
        self.ax = self.canvas.figure.add_subplot(111)

        self.numberOfSamplesLabel = QLabel("N:", self.centralWidget())
        self.numberOfSamplesLabel.setGeometry(450, 300, 120, 30)

        self.numberOfSamples = QLineEdit(self.centralWidget())
        self.numberOfSamples.setGeometry(550, 300, 120, 30)
        self.numberOfSamples.setText("50")  # Default number of samples

        self.SamplesTimeLabel = QLabel("Ts[ms]:", self.centralWidget())
        self.SamplesTimeLabel.setGeometry(450, 350, 120, 30)

        self.SamplesRateValue = QLineEdit(self.centralWidget())
        self.SamplesRateValue.setGeometry(550, 350, 120, 30)
        self.SamplesRateValue.setText("10")  # Default number of samples


    def stop_sampling(self):
        """Send command to stop sampling and stop the thread."""
        self.send_serial_data('g')
        if hasattr(self, 'reader_thread') and self.reader_thread.isRunning():
            self.reader_thread.stop()
            self.reader_thread.wait()


    def start_sampling(self):
        self.serial_conn.reset_input_buffer()
        self.send_sample_time()
        self.serial_conn.reset_input_buffer()
        time.sleep(0.01)
        self.send_serial_data('r')
        samples = int(self.numberOfSamples.text())
        self.times = [ ]
        self.adc_values = [ ]
        self.ax.clear()
        self.line, = self.ax.plot([ ], [ ], color='b')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('ADC Value')
        self.ax.set_title('Sampled Signal')
        self.ax.xaxis.set_major_locator(AutoLocator())
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.ax.yaxis.set_major_locator(MultipleLocator(0.5))
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        self.canvas.draw()
        self.reader_thread = SerialReaderThread(self.serial_conn, samples)
        self.reader_thread.data_point.connect(self.update_plot_realtime)
        self.reader_thread.finished.connect(self.on_data_collection_finished)
        self.reader_thread.start()

    def update_plot_realtime(self, t, val):
        self.times.append(t)
        self.adc_values.append(val)
        self.line.set_data(self.times, self.adc_values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def on_data_collection_finished(self, times, adc_values):
        self.send_serial_data('g')
        df = pd.DataFrame({'Time': times, 'ADC_Value': adc_values})
        df.to_excel('output.xlsx', index=False)
        print("Data exported to output.xlsx")


    def send_serial_data(self, data):
        if not self.serial_conn or not self.serial_conn.is_open:
            print("No active serial connection.")
            return
        try:
            self.serial_conn.write(data.encode())
            print(f"Sent '{data}' to microcontroller.")
        except Exception as e:
            print(f"Error sending data: {e}")

    def send_sample_time(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            print("No active serial connection.")
            return
        try:
            sample_time = int(self.SamplesRateValue.text())  # QLineEdit for sample time
            self.serial_conn.write(f"{sample_time}\n".encode())  # Send as string with newline
            print(f"Sent sample time: {sample_time}")
        except Exception as e:
            print(f"Error sending sample time: {e}")

    def read_serial_data(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            print("No active serial connection.")
            return
        try:
            samples = int(self.numberOfSamples.text())  # Get sample count from textbox
            count = 0
            adc_values = [ ]
            times = [ ]

            while count < samples:
                line = self.serial_conn.readline().decode().strip()
                if line:
                    parts = line.split(',')
                    # print(f"Split data: {parts}")
                    val = float(parts[0])  # Convert first part to float to ensure it's a valid ADC value
                    t = float(parts[ 1 ])  # Convert first part to float to ensure it's a valid Time value
                    adc_values.append(val/(2**16)*3.3) # Assuming first part is ADC value
                    times.append(t/1000)  # Assuming second part is time in milliseconds, convert to seconds and scale ADC value

                    count += 1
                else:
                    time.sleep(0.001)  # Small delay if no data
            self.send_serial_data('g')  # Stop sampling
            df = pd.DataFrame({'Time': times, 'ADC_Value': adc_values})
            df.to_excel('output.xlsx', index=False)  # Export to Excel
            print("Data exported to output.xlsx")
            self.plot_signal(df)  # Plot the signal
            # print(df)
        except Exception as e:
            print(f"Error reading data: {e}")

    # def set_xscale(self):
    #     text = self.xscale_input.text()
    #     try:
    #         start, end = map(float, text.split(','))
    #         self.xscale = (start, end)
    #         # Re-plot with new scale if data exists
    #         if hasattr(self, 'last_df'):
    #             self.plot_signal(self.last_df)
    #     except Exception as e:
    #         print(f"Invalid x-axis range: {e}")

    def plot_signal(self, df):
        self.ax.clear()
        self.ax.plot(df[ 'Time' ], df[ 'ADC_Value' ])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('ADC Value')
        self.ax.set_title('Sampled Signal')
        self.ax.xaxis.set_major_locator(AutoLocator())  # Automatic major ticks
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(5))  # Minor ticks
        self.ax.yaxis.set_major_locator(MultipleLocator(0.5))  # Adjust as needed
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        self.canvas.draw()


    def refresh_com_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_combo.clear()
        self.com_combo.addItems(ports if ports else ["No ports found"])

    def connect_to_microcontroller(self):
        baud = int(self.baud_combo.currentText())
        com = self.com_combo.currentText()
        try:
            self.serial_conn = serial.Serial(com, baud, timeout=1)
            self.serial_conn.reset_input_buffer()  # Clear old data
            print(f"Connected to {com} at {baud} baud.")
            self.toggle_red_btn.setEnabled(True)  # Enable SAMPLE
            self.toggle_green_btn.setEnabled(True)  # Enable STOP

            self.send_serial_data('g')  # This will send a stop the uC from sampling
        except Exception as e:
            print(f"Error connecting: {e}")

    def disconnect_from_microcontroller(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.send_serial_data('g')  # This will send a stop the uC from sampling
            self.serial_conn.close()
            print("Disconnected from microcontroller.")
            self.serial_conn = None
            self.toggle_red_btn.setEnabled(False)  # Disable SAMPLE
            self.toggle_green_btn.setEnabled(False)  # Disable STOP

        else:
            print("No active connection to disconnect.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())