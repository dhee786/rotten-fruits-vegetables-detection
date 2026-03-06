from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import threading
import time
import os
from tensorflow.keras.models import load_model

app = Flask(__name__)
latest_result = "Waiting..."
latest_confidence = 0

# LOAD MODEL

MODEL_PATH = "rotten_model.h5"
model = load_model(MODEL_PATH)
print("Model Loaded ✅")

# Auto detect input size
input_shape = model.input_shape
IMG_HEIGHT = input_shape[1]
IMG_WIDTH = input_shape[2]

print("Model Input Size:", IMG_HEIGHT, "x", IMG_WIDTH)

# LOAD CLASS NAMES (Correct Path)

DATASET_PATH = "dataset/Train"

class_names = sorted([
    folder for folder in os.listdir(DATASET_PATH)
    if os.path.isdir(os.path.join(DATASET_PATH, folder))
])

print("Classes Found:", class_names)

# GLOBAL VARIABLES

latest_label = "No Fruit Detected"
latest_confidence = 0
frame_for_prediction = None

THRESHOLD = 75   # Confidence threshold
PREDICTION_DELAY = 0.2

# BACKGROUND PREDICTION LOOP

def predict_loop():
    global latest_label, latest_confidence, frame_for_prediction

    while True:
        if frame_for_prediction is not None:
            try:
                frame = frame_for_prediction.copy()

                img = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
                img = img / 255.0
                img = np.reshape(img, (1, IMG_HEIGHT, IMG_WIDTH, 3))

                prediction = model.predict(img, verbose=0)

                index = np.argmax(prediction)
                confidence = float(np.max(prediction))
                confidence_percent = confidence * 100

                if confidence_percent < THRESHOLD:
                    latest_label = "No Fruit Detected"
                    latest_confidence = 0
                else:
                    latest_label = class_names[index]
                    latest_confidence = round(confidence_percent, 2)

            except Exception as e:
                print("Prediction Error:", e)

        time.sleep(PREDICTION_DELAY)

# CAMERA STREAM

def generate_frames():
    global frame_for_prediction

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera not opening ❌")
        return

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame_for_prediction = frame

        display_text = f"{latest_label} ({latest_confidence}%)"

        cv2.putText(frame, display_text,
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame +
               b'\r\n')

    camera.release()

# ROUTES
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/result")
def result():
    return jsonify({
        "label": latest_result,
        "confidence": latest_confidence
    })
    
@app.route("/detect")
def detect():
    return jsonify({
        "name": latest_result,
        "confidence": latest_confidence
    })

# Start background prediction thread
threading.Thread(target=predict_loop, daemon=True).start()

# RUN APP

if __name__ == '__main__':
    app.run(debug=True)