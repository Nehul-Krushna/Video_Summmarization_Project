import unittest
from app import create_app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()

    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_upload_route_with_valid_file(self):
        with open('testing_files/valid_video.mp4', 'rb') as file:
            data = {'file': (file, 'valid_video.mp4')}
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)

    def test_upload_route_with_invalid_file(self):
        with open('testing_files/invalid_video.txt', 'rb') as file:
            data = {'file': (file, 'invalid_video.txt')}
            response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)  # Change this to the expected response code for invalid files

    def test_upload_route_with_valid_URL(self):
        data = {'video_url': 'https://www.youtube.com/watch?v=ukzFI9rgwfU'}
        response = self.app.post('/upload', data=data)
        self.assertEqual(response.status_code, 200)

    def test_upload_route_with_invalid_URL(self):
        data = {'video_url': 'invalid_video_url'}
        response = self.app.post('/upload', data=data)
        self.assertEqual(response.status_code, 200)  # Change this to the expected response code for invalid URLs

if __name__ == '__main__':
    unittest.main()