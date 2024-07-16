import tensorflow.keras
import tensorflow as tf
from PIL import Image
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
import boto3
import io
import json

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load models once, outside of the prediction function
model_paths = {
    "Boron": 'b-h-1000.h5',
    "Calcium": 'ca-h-500.h5',
    "Iron": 'fe-h-1000.h5',
    "Potassium": 'k-h-500.h5',
}
models = {element: tensorflow.keras.models.load_model(path, compile=False) for element, path in model_paths.items()}


def load_and_predict(image, model, classes):
    image = img_to_array(image)
    image = tf.image.resize(image, (150, 150))
    image = image / 255.0
    proba = model.predict(image.numpy().reshape(1, 150, 150, 3))
    return {classes[i]: float(proba[0][i]) for i in range(min(len(classes), proba.shape[1]))}


def download_image_from_s3(bucket_name, image_key, aws_access_key_id, aws_secret_access_key):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    image_obj = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_data = image_obj['Body'].read()
    image = Image.open(io.BytesIO(image_data))
    return image


def example(bucket_name, image_key, aws_access_key_id, aws_secret_access_key):
    image = download_image_from_s3(bucket_name, image_key, aws_access_key_id, aws_secret_access_key)

    results = {}
    deficiencies = []

    for deficiency, model in models.items():
        classes = ["Deficient", "Healthy"]
        element_predictions = load_and_predict(image, model, classes)

        result_deficiency = max(element_predictions, key=element_predictions.get)
        confidence = max(element_predictions.values())

        results[deficiency] = {
            "Deficient": float(element_predictions["Deficient"]),
            "Healthy": float(element_predictions["Healthy"]),
            "Deficiency": result_deficiency
        }
        deficiencies.append((deficiency, result_deficiency, confidence))

    # Determine the most likely deficiency
    most_likely_deficiency = max(deficiencies, key=lambda item: item[2])

    results['Most_Likely_Deficiency'] = {
        'Type': most_likely_deficiency[0],
        'Health_Status': most_likely_deficiency[1],
        'Confidence': float(most_likely_deficiency[2])
    }

    return json.dumps(results)