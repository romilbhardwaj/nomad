import unittest
import  docker

class TestDockerSDK(unittest.TestCase):
    def setUp(self):
        self.client = docker.from_env()

    def test_list_images(self):
        print(self.client.images.list())

    def test_build_image(self):
        #img = docker.build('Dockerfile', build_args)
        pass




if __name__ == '__main__':
    unittest.main()