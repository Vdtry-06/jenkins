import unittest
from app import app

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_add_numbers(self):
        response = self.app.get('/add?num1=3&num2=5')
        data = response.get_json()
        self.assertEqual(data['result'], 8)

    def test_invalid_input(self):
        response = self.app.get('/add?num1=abc&num2=5')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()