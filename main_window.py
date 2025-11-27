import sys
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

from model_worker import ModelWorker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("YOLO Waste Detection App")
        self.setGeometry(200, 200, 900, 600)

        # Video display area
        self.video_label = QLabel("Camera Feed Will Appear Here")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #333; color: white;")
        self.video_label.setFixedHeight(400)

        # Buttons
        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.exit_button = QPushButton("Exit")

        # Simple style
        for btn in [self.start_button, self.stop_button, self.exit_button]:
            btn.setFixedHeight(40)
            btn.setFont(QFont("Arial", 12))

        # Dropdown + Slider
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems([r"C:\Users\User\Desktop\dekstop_application_deployment\waste_yolo.pt"])  # you can add more models here

        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(0)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(30)

        # Layouts
        side_layout = QVBoxLayout()
        side_layout.addWidget(QLabel("Model Selection:"))
        side_layout.addWidget(self.model_dropdown)
        side_layout.addWidget(QLabel("Confidence Threshold:"))
        side_layout.addWidget(self.confidence_slider)
        side_layout.addWidget(self.start_button)
        side_layout.addWidget(self.stop_button)
        side_layout.addWidget(self.exit_button)
        side_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 4)
        main_layout.addLayout(side_layout, 1)

        self.setLayout(main_layout)

        # Connect events
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.exit_button.clicked.connect(self.close)

    def start_camera(self):
        if self.worker is None:
            model_path = self.model_dropdown.currentText()
            conf = self.confidence_slider.value() / 100

            self.worker = ModelWorker(model_path, conf)
            self.worker.frame_signal.connect(self.update_frame)
            self.worker.start()

    def stop_camera(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            self.video_label.setText("Camera Stopped")

    def update_frame(self, qt_image):
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()