import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from essay_request import app, get_response

class EssayRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('essay_request.Prompty.load')
    @patch('essay_request.AzureOpenAIModelConfiguration')
    def test_get_response(self, mock_azure_config, mock_prompty_load):
        mock_prompty_instance = MagicMock()
        mock_prompty_instance.return_value = "mocked_result"
        mock_prompty_load.return_value = mock_prompty_instance

        file_path = os.path.join(os.path.dirname(__file__), 'essay.sample.json')
        with open(file_path, 'r') as file:
            essay_eval_request = json.load(file)

        response = get_response(essay_eval_request)
        self.assertEqual(response, {"essay_evaluation_result": "mocked_result"})

    @patch('essay_request.get_response')
    def test_essay_endpoint(self, mock_get_response):
        mock_get_response.return_value = {"essay_evaluation_result": "mocked_result"}

        essay_eval_request = {
            "language": "English",
            "genre": "Narrative",
            "statement": "This is a test statement.",
            "title": "Test Title",
            "essay": "This is a test essay.",
            "support_text": "This is support text.",
            "skills": ["skill1", "skill2"]
        }

        response = self.app.post('/essay', data=json.dumps(essay_eval_request), content_type='application/json')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, {"essay_evaluation_result": "mocked_result"})

if __name__ == '__main__':
    unittest.main()