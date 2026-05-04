from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton,
                             QTextEdit, QVBoxLayout, QHBoxLayout,
                             QSpinBox, QDoubleSpinBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Import the helper that lives in the transmitter file
from RC_Car_Control_II_transmitter import formatTwoWordData

class CalibrationWindow(QDialog):
    """A separate dialog window for accelerometer calibration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accelerometer Calibration")
        self.setFixedSize(500, 400)

        # --- Title label ---
        title = QLabel("Accelerometer Calibration", self)
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # --- Calibration log ---
        self.cal_log = QTextEdit(self)
        self.cal_log.setReadOnly(True)
        self.cal_log.setPlaceholderText("Calibration output will appear here...")

        # --- Buttons ---
        self.start_cal_btn = QPushButton("Start Calibration", self)
        self.start_cal_btn.clicked.connect(self.start_calibration)

        self.clear_log_btn = QPushButton("Clear Log", self)
        self.clear_log_btn.clicked.connect(self.cal_log.clear)

        self.close_btn = QPushButton("Close", self)
        self.close_btn.clicked.connect(self.close)

        # --- Layout ---
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_cal_btn)
        btn_layout.addWidget(self.clear_log_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(self.cal_log)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def start_calibration(self):
        """Send the CAL command over UART via the parent MainWindow."""
        main_window = self.parent()
        self.cal_log.append("Starting calibration...")

        # Guard: make sure the serial port is open before sending
        if main_window is None or main_window.serial_port is None or not main_window.serial_port.is_open:
            self.cal_log.append("ERROR: No serial port connected.")
            return

        cmd = formatTwoWordData("CAL")
        main_window.send_serial_data(cmd)
        self.cal_log.append("Sent: CAL")

