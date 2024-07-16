import json

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from analyze import example
import os

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")


@app.post("/")
def calculate_nutrients():
    #print(request)
    requestObj = request.json['name']
    #print(requestObj)
    image_key = requestObj
    print(image_key)
    result = example(os.getenv('AWS_BUCKET_NAME'), image_key, os.getenv('AWS_ACCESS_KEY_ID'),
                     os.getenv('AWS_SECRET_ACCESS_KEY'))
    print("result ", result)
    return jsonify(json.loads(result))
