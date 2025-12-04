import cv2
from ultralytics import YOLO
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class ModelWorker(QThread):
    frame_signal = Signal(QImage)
    detection_signal = Signal(list) 

    def __init__(self, model_path, confidence=0.3):
        super().__init__()
        self.model = YOLO(model_path)
        self.conf_threshold = confidence
        self.running = True

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

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model.predict(img, verbose=False)
            
            current_frame_detections = set()

            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf < self.conf_threshold:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    class_name = self.waste_class[cls_id]
                    
                    current_frame_detections.add(class_name)

                    label = f"{class_name} ({conf*100:.1f}%)"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (0, 255, 0), 2)
            
            self.detection_signal.emit(list(current_frame_detections))
            
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