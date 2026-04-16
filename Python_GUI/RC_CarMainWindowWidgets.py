from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QComboBox, QPushButton, QTextEdit,
                             QSlider, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, Qt, QTimer

class MainWindowWidgetSetup:
    @staticmethod
    def setup_textbox_messages(main_window):
        # setGeometry(x, y, width, height)
        # x: distance from the left edge of the window (in pixels)
        # y: distance from the top edge of the window (in pixels)
        # width: width of the text box (in pixels)
        # height: height of the text box (in pixels)

        # The message box to show what was transmitted.
        main_window.tx_label = QLabel("Transmitted Data:", main_window)
        main_window.tx_label.setGeometry(20, 225, 400, 25)
        main_window.text_box = QTextEdit(main_window)
        main_window.text_box.setGeometry(20, 250, 400, 200)
        main_window.text_box.setReadOnly(True)

        # The message to display the data received from the transmitter MCU.
        main_window.rx_label = QLabel("Received Data:", main_window)
        main_window.rx_label.setGeometry(500, 225, 400, 25)
        main_window.RxText_box = QTextEdit(main_window)
        main_window.RxText_box.setGeometry(450, 250, 450, 200)
        main_window.RxText_box.setReadOnly(True)
        main_window.rx_data_signal.connect(main_window.append_rx_text)

        bold_font = QFont()
        bold_font.setBold(True)
        main_window.tx_label.setFont(bold_font)
        main_window.rx_label.setFont(bold_font)

    @staticmethod
    def setup_uart_widgets(main_window):
        main_window.baud_label = QLabel("Select Baud Rate:", main_window)
        main_window.baud_label.setGeometry(20, 20, 120, 30)

        main_window.baud_combo = QComboBox(main_window)
        main_window.baud_combo.setGeometry(150, 20, 150, 30)
        main_window.baud_combo.addItems([
            "9600", "19200", "38400", "57600", "115200"])

        main_window.com_label = QLabel("Select COM Port:", main_window)
        main_window.com_label.setGeometry(20, 70, 120, 30)

        main_window.com_combo = QComboBox(main_window)
        main_window.com_combo.setGeometry(150, 70, 150, 30)
        # The main window should call refresh_com_ports after setup

        main_window.refresh_btn = QPushButton("Refresh", main_window)
        main_window.refresh_btn.setGeometry(320, 70, 120, 30)
        main_window.refresh_btn.clicked.connect(main_window.refresh_com_ports)

        main_window.connect_btn = QPushButton("Connect", main_window)
        main_window.connect_btn.setGeometry(100, 130, 120, 40)
        main_window.connect_btn.clicked.connect(main_window.connect_to_microcontroller)

        main_window.disconnect_btn = QPushButton("Disconnect", main_window)
        main_window.disconnect_btn.setGeometry(300, 130, 120, 40)
        main_window.disconnect_btn.clicked.connect(main_window.disconnect_com_port)

    @staticmethod
    def setup_pwm_widgets(main_window):
        # Add slider for motor speed control
        main_window.pwm_label = QLabel("PWM value: 0", main_window)
        main_window.pwm_label.setGeometry(20, 190, 120, 30)

        # Corrected the QSlider orientation by explicitly using Qt.Orientation.Horizontal
        main_window.pwm_slider = QSlider(Qt.Orientation.Horizontal, main_window)
        main_window.pwm_slider.setGeometry(150, 190, 400, 30)
        main_window.pwm_slider.setRange(0, 65535)  # use 0-100 if your MCU expects ticks (0-65535)
        main_window.pwm_slider.setTickInterval(25)
        main_window.pwm_slider.setEnabled(False)  # enabled when connected
        main_window.pwm_slider.valueChanged.connect(main_window.on_pwm_change)

        # Direction radio buttons: Disabled / Forward / Backward
        main_window.dir_disabled_rb = QRadioButton("Disabled", main_window)
        main_window.dir_disabled_rb.setGeometry(570, 180, 100, 30)
        main_window.dir_forward_rb = QRadioButton("Forward", main_window)
        main_window.dir_forward_rb.setGeometry(570, 205, 100, 30)
        main_window.dir_backward_rb = QRadioButton("Backward", main_window)
        main_window.dir_backward_rb.setGeometry(680, 205, 100, 30)

        main_window.dir_group = QButtonGroup(main_window)
        main_window.dir_group.addButton(main_window.dir_disabled_rb)
        main_window.dir_group.addButton(main_window.dir_forward_rb)
        main_window.dir_group.addButton(main_window.dir_backward_rb)

        # Start with Disabled selected and everything disabled until connected
        main_window.dir_disabled_rb.setChecked(True)
        main_window.dir_disabled_rb.setEnabled(False)
        main_window.dir_forward_rb.setEnabled(False)
        main_window.dir_backward_rb.setEnabled(False)
        main_window.current_direction = None  # 'F' or 'B' or None

        # Connect radio button changes
        main_window.dir_group.buttonClicked.connect(main_window.on_direction_change)

        # Since there was an issue with UART Receive from responding too quickly to slider changes,
        # debouncing mechanism is added to limit the rate of sending commands.
        main_window._last_pwm_value = 0
        main_window.pwm_debounce_timer = QTimer(main_window)
        main_window.pwm_debounce_timer.setSingleShot(True)
        main_window.pwm_debounce_timer.setInterval(10)  # ms; adjust to taste
        main_window.pwm_debounce_timer.timeout.connect(main_window.send_debounced_pwm)
        main_window.pwm_slider.sliderReleased.connect(main_window.on_slider_released)
