from flask import Flask
from flask import request

app = Flask(__name__)

@app.post("/")
def hello_world():
    requestObj = request.get_json()
    print(requestObj['name'])
    print(requestObj['password'])
    return "<p>Hello, Chandrababu Gowda</p>"