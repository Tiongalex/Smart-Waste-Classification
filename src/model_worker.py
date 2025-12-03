import cv2
from ultralytics import YOLO
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class ModelWorker(QThread):
    frame_signal = Signal(QImage)
    detection_signal = Signal(str)

    def __init__(self, model_path, confidence=0.3):
        super().__init__()
        self.model = YOLO(model_path)
        self.conf_threshold = confidence
        self.running = True

        # Class names
        self.waste_class = ["Battery", "Biological", "Cardboard", "Clothes", "Glass",
                            "Metal", "Paper", "Plastic", "Shoes", "Trash"]

    def run(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert BGR → RGB
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # YOLO prediction
            results = self.model.predict(img, verbose=False)
            
            detected_class = None

            # Draw boxes (same logic as your script)
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf < self.conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    label = f"{self.waste_class[cls_id]} ({conf*100:.1f}%)"

                    detected_class = self.waste_class[cls_id]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (0, 255, 0), 2)
            if detected_class:
                self.detection_signal.emit(detected_class)
            
            # Convert to QImage for PySide6
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.frame_signal.emit(qt_image)

        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()