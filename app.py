import json

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from analyze import example
import os

load_dotenv()

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)

@app.post("/")
def calculate_nutrients():
    requestObj = request.get_json()
    image_key = requestObj['name']
    result = example(os.getenv('AWS_BUCKET_NAME'), image_key, os.getenv('AWS_ACCESS_KEY_ID'),
                     os.getenv('AWS_SECRET_ACCESS_KEY'))
    return jsonify(json.loads(result))
