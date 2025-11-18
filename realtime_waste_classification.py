import cv2
import numpy as np
import tensorflow as tf

# Load model
model_path = r"C:\Users\User\Desktop\SmartWasteClass\models\waste_model.keras"
model = tf.keras.models.load_model(model_path)

# Class names
waste_class = ["Battery", "Biological", "Cardboard", "Clothes", "Glass",
               "Metal", "Paper", "Plastic", "Shoes", "Trash"]

# Start webcam
cap = cv2.VideoCapture(0)  # 0 = default webcam

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocessing same as training
    img = cv2.resize(frame, (224, 224))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    # Predict
    preds = model.predict(img, verbose=0)
    class_id = np.argmax(preds)
    confidence = np.max(preds)

    label = f"{waste_class[class_id]} ({confidence*100:.2f}%)"

    # Display text on screen
    cv2.putText(frame, label, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Real-Time Waste Classification", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
