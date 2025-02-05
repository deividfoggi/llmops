import unittest
from token_usage import TokenTrackingEvaluator

class MockEvaluator:
    def evaluate(self, *args, **kwargs):
        return {'usage': {'total_tokens': 10}}

class TestTokenTrackingEvaluator(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator = MockEvaluator()
        self.token_tracking_evaluator = TokenTrackingEvaluator(self.mock_evaluator)

    def test_initial_total_tokens(self):
        self.assertEqual(self.token_tracking_evaluator.total_tokens, 0)

    def test_evaluate_updates_total_tokens(self):
        result = self.token_tracking_evaluator.evaluate()
        self.assertEqual(result, {'usage': {'total_tokens': 10}})
        self.assertEqual(self.token_tracking_evaluator.total_tokens, 10)

    def test_evaluate_multiple_times(self):
        self.token_tracking_evaluator.evaluate()
        self.token_tracking_evaluator.evaluate()
        self.assertEqual(self.token_tracking_evaluator.total_tokens, 20)

if __name__ == '__main__':
    unittest.main()