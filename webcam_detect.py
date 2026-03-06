import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# trained model load
model = load_model("rotten_model.h5")

# ⭐ dataset se automatic classes load
datagen = ImageDataGenerator(rescale=1./255)

data = datagen.flow_from_directory(
    "dataset/train",
    target_size=(150,150),
    batch_size=1,
    class_mode="categorical",
    shuffle=False
)

classes = list(data.class_indices.keys())
print("Detected Classes:", classes)

# webcam start
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # preprocess frame
    img = cv2.resize(frame,(150,150))
    img = img/255.0
    img = np.reshape(img,[1,150,150,3])

    # prediction
    pred = model.predict(img, verbose=0)
    predicted_class = classes[np.argmax(pred)]
    confidence = np.max(pred)
    class_index = np.argmax(pred)
    
    global latest_result, latest_confidence
    latest_result = predicted_class
    latest_confidence = round(float(confidence * 100), 2)

    # confidence check
    if confidence < 0.7:
        label = "No Fruit Detected"
    else:
        label = classes[class_index]

    # show result
    cv2.putText(frame,f"{label} ({confidence:.2f})",(20,40),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    cv2.imshow("Rotten Fruit Detection",frame)

    if cv2.waitKey(1) == 27:  # ESC exit
        break

cap.release()
cv2.destroyAllWindows()