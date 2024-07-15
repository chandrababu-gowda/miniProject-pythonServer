import tensorflow.keras
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from keras._tf_keras.keras.preprocessing.image import img_to_array
import boto3
import io
import json

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

def example(bucket_name, image_key, aws_access_key_id, aws_secret_access_key):
    # Load the model
    keras_model = tensorflow.keras.models.load_model('b-h-1000.h5', compile=False)
    keras_model._name = 'model1'

    classes1 = ["Boron", "Healthy"]

    temp = {}
    # Download image from S3
    image = download_image_from_s3(bucket_name, image_key, aws_access_key_id, aws_secret_access_key)
    # Convert image to NumPy array and resize to (150, 150)
    image = img_to_array(image)
    image = tf.image.resize(image, (150, 150))
    image = image / 255.0

    proba1 = keras_model.predict(image.numpy().reshape(1, 150, 150, 3))
    top_3 = np.argsort(proba1[0])[:-4:-1]
    for i in range(2):
        temp[classes1[top_3[i]]] = proba1[0][top_3[i]]

    pr = []
    cn = []

    for k, v in temp.items():
        pr.append(v)
        cn.append(k)

        if v == max(temp.values()):
            deficiency = k

    result = {cn[i]: float(pr[i]) for i in range(2)}
    result['Deficiency'] = deficiency

    return json.dumps(result)

def download_image_from_s3(bucket_name, image_key, aws_access_key_id, aws_secret_access_key):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    image_obj = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_data = image_obj['Body'].read()
    image = Image.open(io.BytesIO(image_data))
    return image
