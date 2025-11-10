import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model


model = load_model(r"C:\Users\User\Desktop\SmartWasteClass\models\waste_model.keras")

# Load and preprocess the image
img_path = r"C:\Users\User\Desktop\SmartWasteClass\dataset\test1.jpg"
img = image.load_img(img_path, target_size=(256, 256))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)  
img_array = img_array / 255.0  

# Predict
predictions = model.predict(img_array)

# Get predicted class
waste_class = ["Battery", "Biological", "Brown-Glass", "Cardboard", "Clothes", "Green-Glass", "Metal", "Paper", "Plastic", "Shoes", "Trash", "White-Glass"]
predicted_class_index = np.argmax(predictions[0])
print("Predicted class:", waste_class[predicted_class_index])
