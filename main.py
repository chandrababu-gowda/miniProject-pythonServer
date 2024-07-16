import tensorflow.keras
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
import gradio as gr

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)


def load_and_predict(image, model, classes):
    image = img_to_array(image)
    image = tf.image.resize(image, (150, 150))
    image = image / 255.0
    proba = model.predict(image.numpy().reshape(1, 150, 150, 3))
    # Ensure proba has the correct shape
    if proba.shape[1] == 1:
        # If the model outputs a single value, assume it's the probability for the deficiency
        return {classes[0]: float(proba[0][0]), classes[1]: 1 - float(proba[0][0])}
    else:
        # If the model outputs multiple values, use them directly
        return {classes[i]: float(proba[0][i]) for i in range(min(len(classes), proba.shape[1]))}


# Load models once, outside of the prediction function
model_paths = {
    "Boron": 'b-h-1000.h5',
    "Calcium": 'ca-h-500.h5',
    "Iron": 'fe-h-1000.h5',
    "Potassium": 'k-h-500.h5',
}
models = {element: tensorflow.keras.models.load_model(path, compile=False) for element, path in model_paths.items()}


def predict_deficiency(image):
    predictions = {}
    for element, model in models.items():
        classes = [element, "Healthy"]  # Assuming binary classification for each nutrient
        element_predictions = load_and_predict(image, model, classes)
        predictions[element] = element_predictions[element]

    max_element = max(predictions, key=predictions.get)
    formatted_predictions = {k: float(v) for k, v in predictions.items()}

    return formatted_predictions, max_element


# Gradio interface
iface = gr.Interface(
    fn=predict_deficiency,
    inputs=gr.Image(),
    outputs=[
        gr.Label(num_top_classes=5, label="Nutrient Deficiencies"),
        gr.Text(label="Most Likely Deficiency")
    ],
    title="Banana Farm: Deficiency of nutrients in banana leaves",
    description="Upload an image of a banana leaf to detect nutrient deficiencies.",
)

# Launch the interface
iface.launch(share=False, server_name="127.0.0.1", server_port=7860)