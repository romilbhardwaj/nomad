import random
import time
import numpy as np
import cv2
import datetime
import inspect
import os
import nomad
#import picamera
from nomad.demo.nomad_emotion.loader import get_model, preprocess_input

from keras.models import load_model

emotion_classifier = None

def get_model(path='fer2013_mini_XCEPTION.102-0.66.hdf5'):
    global emotion_classifier
    if emotion_classifier is None:
        emotion_classifier = load_model(path, compile=False)
    return emotion_classifier


def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x


# def read_picamera():
#     with picamera.PiCamera() as camera:
#         resolution = camera.resolution
#         camera.framerate = 24
#         image = np.empty((resolution[1] * resolution[0] * 3,), dtype=np.uint8)
#         camera.capture(image, 'bgr')
#         image = image.reshape((resolution[1], resolution[0], 3))
#         return image

def dummy_read_camera():
    return np.ones([480, 640], dtype='uint8')

def read_camera():
    cap = cv2.VideoCapture(0)
    # Capture frame-by-frame
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # When everything done, release the capture
    cap.release()
    return gray

def read_video():
    folder = '/nomad/nomad/demo/videos/'
    files = os.listdir(folder)
    image_path = os.path.join(folder, random.choice(files))
    img = cv2.imread(image_path, 0)
    return img.tolist()

def get_face_boundingbox(image):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(image, 1.3, 5)
    roi_image = None
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_image = image[y:y + h, x:x + w]
    return roi_image

def downsample_image(image):
    return cv2.resize(image, (0,0), fx=0.5, fy=0.5)

def get_face_emotion(face_image):
    if face_image is None:
        emotion_text = "NoFace"
    else:
        emotion_labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'sad', 5: 'surprise', 6: 'neutral'}

        # getting input model shapes for inference
        emotion_classifier = get_model()
        emotion_target_size = emotion_classifier.input_shape[1:3]

        gray_face = cv2.resize(face_image, (emotion_target_size))
        gray_face = preprocess_input(gray_face, False)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        emotion_text = emotion_labels[emotion_label_arg]

    # Write emotion to file with timestamp
    with open("emotion.txt", "a+") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + " " + emotion_text + "\n")
    return emotion_text

if __name__ == '__main__':
    while(True):
        time.sleep(0.1)
        image = read_camera()
        #downsampled_image = downsample_image(image)
        roi_image = get_face_boundingbox(image)
        text = get_face_emotion(roi_image)
        print(text)
        cv2.imshow('image', image)
        cv2.waitKey(1)
