from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.inception_v3 import (
    InceptionV3,
    decode_predictions,
    preprocess_input,
)
from tensorflow.keras.utils import load_img, img_to_array
import tempfile
import os

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]


model = InceptionV3(weights="imagenet", include_top=True)


def classify_image(image_path: str, top_k: int = 5) -> list[dict]:
    img = load_img(image_path, target_size=(299, 299))
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    preds = model.predict(x)
    results = decode_predictions(preds, top=top_k)[0]

    return [
        {"class_id": cid, "label": label, "confidence": float(score)}
        for cid, label, score in results
    ]


def user_exist(username):
    return users.find_one({"Username": username}) is not None


def verify_pw(username, password):
    user = users.find_one({"Username": username})
    if not user:
        return False

    hashed_pw = user["Password"]
    return bcrypt.hashpw(password.encode("utf8"), hashed_pw) == hashed_pw


def generate_return_dictionary(status, msg):
    return {"status": status, "msg": msg}


def verify_credentials(username, password):
    if not user_exist(username):
        return generate_return_dictionary(301, "Invalid username"), True

    if not verify_pw(username, password):
        return generate_return_dictionary(302, "Invalid password"), True

    return None, False


class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if user_exist(username):
            return jsonify(generate_return_dictionary(301, "Invalid username"))

        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        users.insert_one(
            {"Username": username, "Password": hashed_pw, "Tokens": 4}
        )
        return jsonify(
            generate_return_dictionary(200, "You successfully signed up for the API")
        )


class Classify(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        url = postedData["url"]

        retJson, error = verify_credentials(username, password)
        if error:
            return jsonify(retJson)

        user = users.find_one({"Username": username})
        tokens = user["Tokens"]

        if tokens <= 0:
            return jsonify(
                generate_return_dictionary(303, "Not enough tokens! Please refill.")
            )

        # Download image and classify
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.RequestException as e:
            return jsonify(
                generate_return_dictionary(400, f"Could not download image: {e}")
            )

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(r.content)
            tmp_path = f.name

        try:
            predictions = classify_image(tmp_path)
        finally:
            os.unlink(tmp_path)

        users.update_one(
            {"Username": username}, {"$set": {"Tokens": tokens - 1}}
        )

        return jsonify({"status": 200, "predictions": predictions})


api.add_resource(Register, "/register")
api.add_resource(Classify, "/classify")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)