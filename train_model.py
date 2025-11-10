import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Data preprocessing
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,        # randomly rotate images
    width_shift_range=0.1,    # shift horizontally
    height_shift_range=0.1,   # shift vertically
    shear_range=0.1,          # shear transformation
    zoom_range=0.1,           # zoom in/out
    horizontal_flip=True,     # flip images horizontally
    fill_mode='nearest'       # fill in empty pixels after transforms
)

train_data = train_datagen.flow_from_directory(
    r'C:\Users\User\Desktop\SmartWasteClass\dataset\waste_kaggle',
    target_size=(256,256),
    batch_size=32,
    subset='training'
)

val_data = train_datagen.flow_from_directory(
    r'C:\Users\User\Desktop\SmartWasteClass\dataset\waste_kaggle',
    target_size=(256,256),
    batch_size=32,
    subset='validation'
)

# Model structure
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(256,256,3)),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),       # 50% neurons dropped
    layers.Dense(12, activation='softmax')
])

# Compile
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

early_stop = EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True)

checkpoint = ModelCheckpoint('models/waste_model.keras', monitor='val_accuracy', save_best_only=True)

# Train
model.fit(train_data, validation_data=val_data, epochs=30, callbacks=[early_stop, checkpoint])

# Save model
model.save('models/waste_model.keras') 