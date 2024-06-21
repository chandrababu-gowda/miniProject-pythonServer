import json

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from analyze import example
import os

load_dotenv()

app = Flask(__name__)


@app.post("/")
def calculate_nutrients():
    requestObj = request.get_json()
    image_key = requestObj['name']
    result = example(os.getenv('AWS_BUCKET_NAME'), image_key, os.getenv('AWS_ACCESS_KEY_ID'),
                     os.getenv('AWS_SECRET_ACCESS_KEY'))
    return jsonify(json.loads(result))
