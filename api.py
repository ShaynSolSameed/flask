from flask import Flask, make_response
from flask import request, jsonify
import numpy as np
from io import BytesIO
from PIL import Image
import cv2
from keras.preprocessing import image
from keras.applications.efficientnet import preprocess_input
from keras.models import load_model
import pandas as pd
import os
import logging

b1Model = None
detailsDf = None

app = Flask(__name__)

app.config['VALID_API_KEY'] = os.environ.get('VALID_API_KEY')


def checkApiKey(apiKey):
    return apiKey == app.config['VALID_API_KEY']


def resizeAndConcatenate(frontFile, backFile):

    # Read the content of the file object
    frontData = frontFile.read()
    backData = backFile.read()

    # Create a BytesIO object to treat the binary data as a file
    frontImage = Image.open(BytesIO(frontData))
    backImage = Image.open(BytesIO(backData))

    # Set the desired size
    size = (250, 250)

    resizedFront = frontImage.resize(size)
    resizedBack = backImage.resize(size)

    # Convert PIL images to numpy arrays
    frontArray = cv2.cvtColor(np.array(resizedFront), cv2.COLOR_RGB2BGR)
    backArray = cv2.cvtColor(np.array(resizedBack), cv2.COLOR_RGB2BGR)

    # Concatenate images horizontally
    concatedImage = cv2.hconcat([frontArray, backArray])
    concatedImage = Image.fromarray(
        cv2.cvtColor(concatedImage, cv2.COLOR_BGR2RGB))

    return concatedImage


def getDetails(index):

    result = detailsDf[detailsDf['ClassNumber'] == int(index+1)]

    resultDict = result.to_dict(orient='records')[0]
    return (resultDict)


def predictClass(inputImage):

    # preprocess the image
    inputImage = inputImage.resize((240, 240))
    inputImageArray = image.img_to_array(inputImage)
    inputImageArray = np.expand_dims(inputImageArray, axis=0)
    inputImageArray = preprocess_input(inputImageArray)

    prediction = b1Model.predict(inputImageArray)

    predictedClassIndex = np.argmax(prediction, axis=1)

    # Get the confidence level for the predicted class
    confidenceLevel = prediction[0][predictedClassIndex][0]

    result = getDetails(predictedClassIndex[0])
    result['confidenceLevel'] = float(confidenceLevel)

    return (result)


logging.basicConfig(filename='server_logs.log', level=logging.DEBUG)


@app.route('/')
def home():
    return 'hello world!'


@app.route('/postImage', methods=['POST'])
def postImage():
    try:
        logging.info(f"Request: {request.method} {request.path} ")

        apiKey = request.headers.get('key')

        if not apiKey or not checkApiKey(apiKey):
            logging.info(f"Response: {'unauthorized'} - Status Code: 401")
            return jsonify({'error': 'Unauthorized'}), 401
        requestCount = len(os.listdir('static\pics'))

        if 'back' not in request.files:
            logging.info(f"Response: {'no back image'} - Status Code: 400")
            return jsonify({"message": "back image of the coin not recieved"}), 400
        backImage = request.files['back']

        if 'front' not in request.files:
            logging.info(f"Response: {'no front image'} - Status Code: 400")
            return jsonify({"message": "front image of the coin not recieved"}), 400
        frontImage = request.files['front']

        concatedImage = resizeAndConcatenate(frontImage, backImage)

        concatedImage.save(os.path.join(
            "static\\pics", f"{requestCount}.jpg"))

        prediction = predictClass(concatedImage)

        if prediction["confidenceLevel"] > 0.5:
            logging.info(f"Response: {jsonify(prediction)} - Status Code: 201")
            return jsonify(prediction), 201
        else:
            logging.info(
                f"Response: {jsonify(prediction)} - Status Code: 501 - Picture Number{requestCount}")
            return jsonify({"message": "Could not recognize the coin"}), 501
    except Exception as e:
        logging.info(
            f'Response: {jsonify({"internal server error": f"{e}"})} - Status Code: 500')
        return jsonify({"internal server error": f"{e}"}), 500


def setup():
    global b1Model
    global detailsDf

    # Replace with the path to your B1_model weights files
    modelWeightsPath = 'tl_b1_model_v1.weights.best.hdf5'
    detailsDf = pd.read_csv('coinDetail.csv')
    print(os.environ.get('VALID_API_KEY'))

    print('printed')
    # b1Model = load_model(modelWeightsPath)


with app.app_context():
    setup()


if __name__ == '__main__':
    app.run(debug=False)
