import sys
import time
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

from src.model_worker import ModelWorker
from src.database import save_to_database, init_database
from src.ui.history_window import HistoryWindow

class MainWindow(QWidget):
    DETECTION_HOLD_TIME = 5

    def __init__(self):
        super().__init__()
        init_database()
        self.worker = None
        self.current_class = None
        self.first_detection_time = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YOLO Waste Detection App")
        self.setGeometry(200, 200, 900, 600)

        self.video_label = QLabel("Camera Feed Will Appear Here")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #333; color: white;")
        self.video_label.setFixedHeight(400)

        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.history_button = QPushButton("View History")
        self.exit_button = QPushButton("Exit")

        for btn in [self.start_button, self.stop_button, self.history_button, self.exit_button]:
            btn.setFixedHeight(40)
            btn.setFont(QFont("Arial", 12))

        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["waste_yolo.pt"])

        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(0)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(30)

        side_layout = QVBoxLayout()
        side_layout.addWidget(QLabel("Model Selection:"))
        side_layout.addWidget(self.model_dropdown)
        side_layout.addWidget(QLabel("Confidence Threshold:"))
        side_layout.addWidget(self.confidence_slider)
        side_layout.addWidget(self.start_button)
        side_layout.addWidget(self.stop_button)
        side_layout.addWidget(self.history_button)
        side_layout.addWidget(self.exit_button)
        side_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 4)
        main_layout.addLayout(side_layout, 1)

        self.setLayout(main_layout)

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.history_button.clicked.connect(self.open_history_window)
        self.exit_button.clicked.connect(self.close)
    
    def update_conf_label(self, value):
        self.conf_label.setText(f"Confidence: {value}%")

    def open_history_window(self):
        self.history_window = HistoryWindow()
        self.history_window.show()

    def start_camera(self):
        if self.worker is None:
            model_path = self.model_dropdown.currentText()
            conf = self.confidence_slider.value() / 100

            self.worker = ModelWorker(model_path, conf)
            self.worker.frame_signal.connect(self.update_frame)
            self.worker.detection_signal.connect(self.handle_detection)
            self.worker.start()

    def stop_camera(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            self.video_label.setText("Camera Stopped")

    def update_frame(self, qt_image):
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def handle_detection(self, detected_class):
        current_time = time.time()

        if detected_class != self.current_class:
            self.current_class = detected_class
            self.first_detect_time = current_time
            return

        if self.first_detect_time and (current_time - self.first_detect_time >= self.DETECTION_HOLD_TIME):
            save_to_database(detected_class)
            print(f"✓ Saved: {detected_class}")
            
            self.first_detect_time = current_time + 9999

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()