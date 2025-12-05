import os
from ultralytics import YOLO

MODEL_PATH = "models/waste_yolo.pt"  # Path to saved trained model
DATA_YAML = "waste_dataset.yaml"
EPOCHS = 100
IMG_SIZE = 768
BATCH = 16

# Load existing trained model if it exists, otherwise start new YOLOv8n model
if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)    # Load previously trained weights
    resume_flag = False        # Do NOT resume optimizer state
else:
    model = YOLO("yolov8n.yaml")  # Create a new YOLOv8n model from scratch
    resume_flag = False

results = model.train(
    data=DATA_YAML,
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=BATCH,
    pretrained=True,     # Start from pretrained COCO weights
    resume=resume_flag, # Resume training only if explicitly allowed
    save_period=-1,
    save=True,
)

BEST_MODEL_PATH = "runs/detect/train/weights/best.pt"

if os.path.exists(BEST_MODEL_PATH):
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    os.replace(BEST_MODEL_PATH, MODEL_PATH)
    print(f"Best model saved to: {MODEL_PATH}")
else:
    print("Best model not found")
