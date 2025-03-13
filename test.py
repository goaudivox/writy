import unittest
import json
import os
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.api_key = os.getenv('API_KEY')  # Ensure the API_KEY is set in your environment

    def test_execute_code_success(self):
        """Test executing simple code successfully."""
        response = self.app.post('/execute-code',
                             headers={"X-API-KEY": self.api_key},
                             data=json.dumps({"code": "result = 123 + 456"}),
                             content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['result'], 579)  # Expecting the result directly

    def test_execute_code_syntax_error(self):
        """Test handling of syntax errors in code."""
        response = self.app.post('/execute-code',
                             headers={"X-API-KEY": self.api_key},
                             data=json.dumps({"code": "prin('hello world')"}),  # Intentional error
                             content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Expecting a 400 status code for syntax errors

if __name__ == '__main__':
    unittest.main()




    import unittest
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_execute_code_syntax_error(self):
        response = self.app.post('/chat', json={"message": "syntax_error"})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()