import sys
import time
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QComboBox, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont
from src.model_worker import ModelWorker
from src.database import save_to_database, init_database
from src.ui.history_window import HistoryWindow

class MainWindow(QWidget):
    DETECTION_HOLD_TIME = 5

    WASTE_TO_BIN = {
        "Paper": "Recyclable Bin",
        "Cardboard": "Recyclable Bin",
        "Plastic": "Recyclable Bin",
        "Metal": "Recyclable Bin",
        "Glass": "Recyclable Bin",
        "Biological": "Organic Bin",
        "Clothes": "General Waste",
        "Shoes": "General Waste",
        "Trash": "General Waste",
        "Battery": "General Waste"
    }

    def __init__(self):
        super().__init__()
        init_database()
        self.worker = None
        
        self.detection_timers = {} 
        self.save_cooldowns = {} 

        self.clear_message_timer = QTimer()
        self.clear_message_timer.setSingleShot(True)
        self.clear_message_timer.timeout.connect(lambda: self.save_message.setText(""))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Waste Detection")
        self.setGeometry(100, 100, 1000, 700)

        self.video_label = QLabel("Camera Feed Disconnected")
        self.video_label.setObjectName("videoLabel")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.bin_label = QLabel("Waiting for Waste...")
        self.bin_label.setObjectName("binLabel")
        self.bin_label.setAlignment(Qt.AlignCenter)

        self.save_message = QLabel("")
        self.save_message.setObjectName("saveLabel")
        self.save_message.setAlignment(Qt.AlignCenter)

        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["waste_yolo.pt"])
        
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(30)
        self.confidence_slider.valueChanged.connect(self.update_conf_label)
        
        self.start_button = QPushButton("START CAMERA")
        self.start_button.setObjectName("startBtn")
        self.start_button.setCursor(Qt.PointingHandCursor)

        self.stop_button = QPushButton("STOP CAMERA")
        self.stop_button.setObjectName("stopBtn")
        self.stop_button.setCursor(Qt.PointingHandCursor)

        self.history_button = QPushButton("View History")
        self.history_button.setObjectName("historyBtn")
        self.history_button.setCursor(Qt.PointingHandCursor)

        self.exit_button = QPushButton("Exit App")
        self.exit_button.setObjectName("exitBtn")
        self.exit_button.setCursor(Qt.PointingHandCursor)

        self.conf_label = QLabel(f"Confidence Threshold: {self.confidence_slider.value()}%")

        side_layout = QVBoxLayout()
        side_layout.setSpacing(15)
        side_layout.setContentsMargins(20, 10, 20, 20)
        
        side_layout.addWidget(QLabel("AI Model:"))
        side_layout.addWidget(self.model_dropdown)
        side_layout.addWidget(self.conf_label)
        side_layout.addWidget(self.confidence_slider)
        side_layout.addSpacing(20)
        side_layout.addWidget(self.start_button)
        side_layout.addWidget(self.stop_button)
        side_layout.addStretch()
        side_layout.addWidget(self.history_button)
        side_layout.addWidget(self.exit_button)

        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(20, 20, 10, 20)
        video_layout.addWidget(self.video_label, stretch=4)
        video_layout.addWidget(self.bin_label)
        video_layout.addWidget(self.save_message)

        main_layout = QHBoxLayout()
        main_layout.addLayout(video_layout, 70)
        main_layout.addLayout(side_layout, 30) 

        self.setLayout(main_layout)

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.history_button.clicked.connect(self.open_history_window)
        self.exit_button.clicked.connect(self.close)

    def update_conf_label(self, value):
        self.conf_label.setText(f"Confidence Threshold: {value}%")

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
            self.bin_label.setText("Detected bin instructions will appear here.")
            self.detection_timers.clear()

    def update_frame(self, qt_image):
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def handle_detection(self, detected_classes_list):
        current_time = time.time()
        
        if not detected_classes_list:
            self.bin_label.setText("Waiting for waste...")
            self.detection_timers.clear()
            return
        
        display_text = ", ".join(detected_classes_list)
        self.bin_label.setText(f"Detected: {display_text}")

        for item in detected_classes_list:
            if item in self.save_cooldowns:
                if current_time - self.save_cooldowns[item] < 5: 
                    continue
                else:
                    del self.save_cooldowns[item]

            if item not in self.detection_timers:
                self.detection_timers[item] = current_time
            
            elapsed_time = current_time - self.detection_timers[item]
            
            if elapsed_time >= self.DETECTION_HOLD_TIME:
                bin_name = self.WASTE_TO_BIN.get(item, "Unknown Bin")
                save_to_database(item, bin_name)
                
                print(f"✓ Saved: {item} → {bin_name}")
                self.save_message.setText(f"Saved: {item} ({bin_name})") 
                self.clear_message_timer.start(3000)
                
                self.save_cooldowns[item] = current_time
                del self.detection_timers[item]

        active_timers = list(self.detection_timers.keys())
        for tracked_item in active_timers:
            if tracked_item not in detected_classes_list:
                del self.detection_timers[tracked_item]

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()