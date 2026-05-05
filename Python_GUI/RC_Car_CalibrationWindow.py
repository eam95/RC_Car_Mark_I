from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton,
                             QTextEdit, QVBoxLayout, QHBoxLayout,
                             QSpinBox, QDoubleSpinBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer



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

        # --- Status indicator ---
        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)

        # --- Calibration log ---
        self.cal_log = QTextEdit(self)
        self.cal_log.setReadOnly(True)
        self.cal_log.setPlaceholderText("Calibration output will appear here...")


        # --- Buttons ---
        self.start_cal_btn = QPushButton("Start Calibration", self)
        self.start_cal_btn.clicked.connect(self.start_calibration)

        self.stop_cal_btn = QPushButton("Stop Calibration", self)
        self.stop_cal_btn.clicked.connect(self.stop_calibration)
        # self.stop_cal_btn.setEnabled(False)  # Disabled until calibration starts

        # Adding a calibrate button once the data is collected.
        self.calibrate_btn = QPushButton("Calibrate", self)
        self.calibrate_btn.clicked.connect(self.calculate_average)

        self.clear_log_btn = QPushButton("Clear Log", self)
        self.clear_log_btn.clicked.connect(self.cal_log.clear)

        self.close_btn = QPushButton("Close", self)
        self.close_btn.clicked.connect(self.close)

        # --- Layout ---
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_cal_btn)
        btn_layout.addWidget(self.stop_cal_btn)
        btn_layout.addWidget(self.calibrate_btn)  #  Added the calibrate button to the layout
        btn_layout.addWidget(self.clear_log_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.cal_log)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def start_calibration(self):
        """Send the CAL command over UART via the parent MainWindow."""
        # Import the helper that lives in the transmitter file
        from RC_Car_Control_II_transmitter import formatTwoWordData
        main_window = self.parent()
        self.cal_log.append("=== STARTING CALIBRATION ===")

        # Guard: make sure the serial port is open before sending
        if main_window is None or main_window.serial_port is None or not main_window.serial_port.is_open:
            self.cal_log.append("ERROR: No serial port connected.")
            return

        # CLEAR THE SERIAL INPUT BUFFER FIRST
        try:
            main_window.serial_port.reset_input_buffer()
            self.cal_log.append("Cleared serial input buffer")
        except Exception as e:
            self.cal_log.append(f"Warning: Could not clear buffer: {e}")

        # Set calibration mode flag
        self.cal_log.append(f"Setting is_calibration_active = True")
        main_window.is_calibration_active = True

        if hasattr(main_window, 'reader_thread') and main_window.reader_thread.isRunning():
            self.cal_log.append(f"Calling reader_thread.set_calibration_mode(True)")
            main_window.reader_thread.set_calibration_mode(True)
            self.cal_log.append(f"Thread mode now: {main_window.reader_thread.calibration_mode}")
        else:
            self.cal_log.append("WARNING: reader_thread not available or not running!")

        # Update UI
        self.status_label.setText("Status: Calibration Active")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

        # Send CAL command to MCU
        cmd = formatTwoWordData("CAL")
        main_window.send_serial_data(cmd)
        self.cal_log.append("Sent: CAL")

        # Wait a moment for MCU to process, then clear buffer again

        QTimer.singleShot(100, lambda: self._post_start_cleanup(main_window))
        # Update main window status
        if hasattr(main_window, 'cal_status_label'):
            main_window.cal_status_label.setText("⚠ CALIBRATION ACTIVE - Plotting Disabled")

        if hasattr(main_window, "reset_calibration_buffers"):
            main_window.reset_calibration_buffers()
            self.cal_log.append("Cleared previous calibration samples")

    def _post_start_cleanup(self, main_window):
        """Clean up any stale data after MCU starts calibration."""
        try:
            if main_window.serial_port and main_window.serial_port.is_open:
                main_window.serial_port.reset_input_buffer()
                self.cal_log.append("Cleared buffer after MCU start")
        except:
            pass

    def stop_calibration(self):
        """Stop calibration mode."""
        from RC_Car_Control_II_transmitter import formatTwoWordData
        main_window = self.parent()
        self.cal_log.append("=== STOPPING CALIBRATION ===")

        if main_window is None:
            self.cal_log.append("ERROR: No parent window!")
            return

        # Send stop command to MCU FIRST
        if main_window.serial_port and main_window.serial_port.is_open:
            cmd = formatTwoWordData("STOP_CAL")
            main_window.send_serial_data(cmd)
            self.cal_log.append("Sent: STOP_CAL")

        # Wait a moment for MCU to process

        QTimer.singleShot(200, lambda: self._finish_stop(main_window))

    def calculate_average(self):
        main_window = self.parent()
        if main_window is None:
            self.cal_log.append("ERROR: No parent window.")
            return

        result = main_window.compute_calibration_average(min_samples=20)
        if result is None:
            count = len(main_window.buf_ax_cal) if hasattr(main_window, "buf_ax_cal") else 0
            self.cal_log.append(f"Not enough samples to calibrate ({count}/20 minimum).")
            return

        self.cal_log.append("=== CALIBRATION RESULTS ===")
        self.cal_log.append(f"Samples: {result['n']}")
        self.cal_log.append(
            f"  ax: avg={result['ax_avg']:+.2f} mg  "
            f"std={result['ax_std']:.2f} mg  "
            f"err={result['ax_pct']:.1f}%"
        )
        self.cal_log.append(
            f"  ay: avg={result['ay_avg']:+.2f} mg  "
            f"std={result['ay_std']:.2f} mg  "
            f"err={result['ay_pct']:.1f}%"
        )
        self.cal_log.append(
            f"  az: avg={result['az_avg']:+.2f} mg  "
            f"std={result['az_std']:.2f} mg  "
            f"err={result['az_pct']:.1f}%"
        )
        self.cal_log.append("--- Offsets to apply ---")
        self.cal_log.append(
            f"  ax_offset={result['ax_offset_mg']:+.2f} mg, "
            f"ay_offset={result['ay_offset_mg']:+.2f} mg, "
            f"az_offset={result['az_offset_mg']:+.2f} mg"
        )

        # ── NEW: push summary to main window label ──
        if hasattr(main_window, 'cal_results_label'):
            summary = (
                f"n={result['n']}  "
                f"ax={result['ax_avg']:+.1f}±{result['ax_std']:.1f}mg ({result['ax_pct']:.1f}%)  "
                f"ay={result['ay_avg']:+.1f}±{result['ay_std']:.1f}mg ({result['ay_pct']:.1f}%)  "
                f"az={result['az_avg']:+.1f}±{result['az_std']:.1f}mg ({result['az_pct']:.1f}%)"
            )
            main_window.cal_results_label.setText(summary)
            main_window.cal_results_label.setStyleSheet(
                "color: lime; background-color: #1a1a1a; padding: 2px;"
            )

    def _finish_stop(self, main_window):
        """Complete the stop sequence after MCU has time to respond."""
        # Clear the serial buffer of any remaining calibration data
        try:
            if main_window.serial_port and main_window.serial_port.is_open:
                main_window.serial_port.reset_input_buffer()
                self.cal_log.append("Cleared serial buffer after stop")
        except Exception as e:
            self.cal_log.append(f"Warning: Could not clear buffer: {e}")

        # Clear calibration mode flag
        self.cal_log.append(f"Setting is_calibration_active = False")
        main_window.is_calibration_active = False

        if hasattr(main_window, 'reader_thread') and main_window.reader_thread.isRunning():
            self.cal_log.append(f"Calling reader_thread.set_calibration_mode(False)")
            main_window.reader_thread.set_calibration_mode(False)
            self.cal_log.append(f"Thread mode now: {main_window.reader_thread.calibration_mode}")
        else:
            self.cal_log.append("WARNING: reader_thread not available!")

        # Update UI
        self.status_label.setText("Status: Ready")
        self.status_label.setStyleSheet("")

        self.cal_log.append("Calibration stopped successfully")
        # Clear main window status
        if hasattr(main_window, 'cal_status_label'):
            main_window.cal_status_label.setText("")