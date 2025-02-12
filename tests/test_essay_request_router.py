import unittest
from unittest.mock import patch, MagicMock
from essay_request_router import get_response, app
import json

class TestEssayRequestRouter(unittest.TestCase):

    @patch('essay_request_router.OldEssay')
    @patch('essay_request_router.EssayEvaluationFlow')
    @patch('essay_request_router.AzureOpenAIModelConfiguration')
    def test_essay_request_router_http_response(self, mock_azure, mock_essay_flow, mock_old_essay):
        tester = app.test_client(self)
        # read content from input.json file
        with open('tests/input.json') as f:
            data = json.load(f)
        response = tester.post('/score', json=data)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()