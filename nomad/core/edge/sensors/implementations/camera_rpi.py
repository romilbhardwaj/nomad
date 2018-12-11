from nomad.core.edge.Sensor import Sensor
import picamera
import numpy as np


class CameraRPi(Sensor):
    def __init__(self, resolution=None):
        if not resolution:
            self.resolution = picamera.resolution
        else:
            self.resolution = resolution

    def get_image(self):
        with picamera.PiCamera() as camera:
            camera.resolution = self.resolution
            image = np.empty((self.resolution[1] * self.resolution[0] * 3,), dtype=np.uint8)
            camera.capture(image, 'bgr')
            image = image.reshape((self.resolution[1], self.resolution[0], 3))
            return image