import pickle
import time
import cv2

if __name__ == '__main__':
    read_camera = pickle.load(open('dummy_read_camera.pickle', 'rb'))
    downsample_image = pickle.load(open('downsample_image.pickle', 'rb'))
    get_face_boundingbox = pickle.load(open('get_face_boundingbox.pickle', 'rb'))
    get_face_emotion = pickle.load(open('get_face_emotion.pickle', 'rb'))
    while(True):
        time.sleep(0.5)
        image = read_camera()
        downsampled_image = downsample_image(image)
        roi_image = get_face_boundingbox(downsampled_image)
        text = get_face_emotion(roi_image)
        print(text)
        cv2.imshow('image', downsampled_image)
        cv2.waitKey(1)

'''
import pickle
read_camera = pickle.load(open('/nomad/nomad/tests/operators/dummy_read_camera.pickle', 'rb'))
downsample_image = pickle.load(open('/nomad/nomad/tests/operators/downsample_image.pickle', 'rb'))
get_face_boundingbox = pickle.load(open('/nomad/nomad/tests/operators/get_face_boundingbox.pickle', 'rb'))
get_face_emotion = pickle.load(open('/nomad/nomad/tests/operators/get_face_emotion.pickle', 'rb'))
read_camera = pickle.load(open('/nomad/nomad/tests/operators/read_picamera.pickle', 'rb'))
read_camera = pickle.load(open('/nomad/nomad/tests/operators/read_picamera.pickle','rb'))

x = pickle.load(open('/nomad/nomad/tests/operators/read_picamera_downsampled.pickle','rb'))
'''