import os
import cv2
import pickle
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing import image

image_size   = 224
encoder_path = "trained_model/encoders.pkl"
model_path   = "trained_model/paddy_doctor.keras"

def load_model_and_encoder():
    if not os.path.exists(encoder_path): 
        raise FileNotFoundError("Encoder not found")
    if not os.path.exists(model_path): 
        raise FileNotFoundError("Model not found")

    model = tf.keras.models.load_model(model_path)
    with open(encoder_path, "rb") as f:
        encoders = pickle.load(f)
    return model, encoders

def predict_paddy(paddy_image):
    if isinstance(paddy_image, str):
        img       = image.load_img(paddy_image, target_size=(image_size, image_size))
        img_array = image.img_to_array(img)
    elif isinstance(paddy_image, Image.Image):
        img       = paddy_image.resize((image_size, image_size))
        img_array = image.img_to_array(img)
    elif isinstance(paddy_image, np.ndarray):
        img_rgb   = cv2.cvtColor(paddy_image, cv2.COLOR_BGR2RGB)
        img       = cv2.resize(img_rgb, (image_size, image_size))
        img_array = image.img_to_array(img)
    else:
        raise ValueError("Unsupported image form")
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    model, encoders  = load_model_and_encoder()
    predicted_result = model.predict(img_array)
    disease_idx      = np.argmax(predicted_result[0][0])
    variety_idx      = np.argmax(predicted_result[1][0])
    max_age          = encoders.get("max_age")

    disease_name = encoders["disease_encoder"].inverse_transform([disease_idx])[0]
    variety_name = encoders["variety_encoder"].inverse_transform([variety_idx])[0]
    age          = int(predicted_result[2][0][0] * max_age)

    return{
            "disease": disease_name,
            "disease_confidence": float(np.max(predicted_result[0][0])) * 100,
            "variety": variety_name,
            "age": age }