import random
import time
import numpy as np
import cv2
import datetime
import inspect
import os
#import picamera
from nomad.demo.nomad_emotion.loader import get_model, preprocess_input

def read_picamera_downsampled():
    import picamera
    import numpy as np
    import cv2
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.framerate = 24
        time.sleep(2)
        image = np.empty((240 * 320 * 3,), dtype=np.uint8)
        camera.capture(image, 'bgr')
        image = image.reshape((240, 320, 3))
        cv2.imwrite('/nomad/image.jpg', image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image.tolist()

def read_picamera():
    import picamera
    import numpy as np
    import cv2
    with picamera.PiCamera() as camera:
        camera.resolution = (1920, 1080)
        #resolution = [1920, 1088]
        print(resolution)
        camera.framerate = 24
        image = np.empty((resolution[1] * resolution[0] * 3,), dtype=np.uint8)
        print(image.shape)
        camera.capture(image, 'bgr')
        image = image.reshape((resolution[1], resolution[0], 3))
        cv2.imwrite('/nomad/image.jpg', image)
        return image.tolist()

def dummy_read_camera():
    return np.ones([10, 10], dtype='uint8').tolist()

def read_video():
    folder = '/nomad/nomad/demo/images/'
    files = os.listdir(folder)
    image_path = os.path.join(folder, random.choice(files))
    img = cv2.imread(image_path, 0)
    return img.tolist()

def read_camera():
    cap = cv2.VideoCapture(0)
    # Capture frame-by-frame
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # When everything done, release the capture
    cap.release()
    return gray.tolist()

def downsample_image(image):
    image = np.array(image, dtype='uint8')
    print(image.shape)
    cv2.imwrite('/nomad/image.jpg', image)
    return cv2.resize(image, (0,0), fx=0.9, fy=0.9).tolist()

def get_face_boundingbox(image):
    image = np.array(image, dtype='uint8')
    print(image.shape)
    cv2.imwrite('/nomad/image.jpg', image)
    face_cascade = cv2.CascadeClassifier('/nomad/nomad/haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(image, 1.3, 5)
    print(faces)
    if not len(faces):
        return []
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_image = image[y:y + h, x:x + w]
        break
    return roi_image.tolist()

def get_face_emotion(face_image):
    if not face_image:
        emotion_text = "NoFace"
    else:
        face_image = np.array(face_image, dtype='uint8')
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
    import cloudpickle
    cloudpickle.dump(read_camera, open('read_camera.pickle', 'wb'))
    cloudpickle.dump(downsample_image, open('downsample_image.pickle', 'wb'))
    cloudpickle.dump(get_face_boundingbox, open('get_face_boundingbox.pickle', 'wb'))
    cloudpickle.dump(get_face_emotion, open('get_face_emotion.pickle', 'wb'))
    cloudpickle.dump(dummy_read_camera, open('dummy_read_camera.pickle', 'wb'))
    cloudpickle.dump(read_picamera, open('read_picamera.pickle', 'wb'))
    cloudpickle.dump(read_picamera_downsampled, open('read_picamera_downsampled.pickle', 'wb'))
    cloudpickle.dump(read_video, open('read_video.pickle', 'wb'))
    # while(True):
    #     time.sleep(0.5)
    #     #image = dummy_read_camera()
    #     image = read_video()
    #     downsampled_image = downsample_image(image)
    #     roi_image = get_face_boundingbox(downsampled_image)
    #     text = get_face_emotion(roi_image)
    #     print(text)
    #     cv2.imshow('image', np.array(downsampled_image, dtype='uint8'))
    #     cv2.waitKey(1)
