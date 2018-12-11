from nomad.core.edge import checks
from nomad.core.edge.sensors.implementations.camera_rpi import CameraRPi


class Camera(object):
    def __init__(self, resolution):
        if checks.is_raspberry_pi():
            return CameraRPi(resolution)

    def get_image(self):
        pass