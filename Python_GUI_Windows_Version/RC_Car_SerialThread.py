from PyQt5.QtCore import QThread, pyqtSignal

class SerialReaderThread(QThread):
    data_received = pyqtSignal(float, float, float, float, float)  # t, x, ax, ay, az
    calibration_data_received = pyqtSignal(float, float, float, float)  # t, ax, ay, az

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self._running = True
        self.calibration_mode = False  # Flag to indicate calibration mode

    def run(self):
        while self._running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode(errors='ignore').strip()
                    data = data.replace('\x00', '').strip()
                    if data:
                        parts = data.split(',')
                        # Check if this is calibration data (4 values) or normal data (5 values)
                        if len(parts) == 4:
                            # Calibration data: t, ax, ay, az
                            t = float(parts[0]) / 1000
                            ax = float(parts[1])
                            ay = float(parts[2])
                            az = float(parts[3])
                            self.calibration_data_received.emit(t, ax, ay, az)
                        elif len(parts) == 5:
                            # Normal data: t, x, ax, ay, az
                            t = float(parts[0]) / 1000
                            x = float(parts[1])
                            ax = float(parts[2])
                            ay = float(parts[3])
                            az = float(parts[4])
                            self.data_received.emit(t, x, ax, ay, az)
                        else:
                            print(f"Unexpected data format: {data}")
            except Exception as e:
                print(f"Skipping bad line: {e}")

    def set_calibration_mode(self, enabled):
        """Set whether we're in calibration mode."""
        self.calibration_mode = enabled

    def stop(self):
        self._running = False
        self.wait()