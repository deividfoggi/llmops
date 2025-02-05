class TokenTrackingEvaluator:
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.total_tokens = 0

    def evaluate(self, *args, **kwargs):
        result = self.evaluator.evaluate(*args, **kwargs)
        self.total_tokens += result['usage']['total_tokens']
        return result