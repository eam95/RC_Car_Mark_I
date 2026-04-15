from PyQt5.QtCore import QThread, pyqtSignal

class SerialReaderThread(QThread):
    data_received = pyqtSignal(float, float, float, float, float)  # t, x, ax, ay, az

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self._running = True

    def run(self):
        while self._running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode(errors='ignore').strip()
                    data = data.replace('\x00', '').strip()
                    if data:
                        parts = data.split(',')
                        t  = float(parts[0])/1000
                        x  = float(parts[1])
                        ax = float(parts[2])
                        ay = float(parts[3])
                        az = float(parts[4])
                        self.data_received.emit(t, x, ax, ay, az)
            except Exception as e:
                print(f"Skipping bad line: {e}")

    def stop(self):
        self._running = False
        self.wait()