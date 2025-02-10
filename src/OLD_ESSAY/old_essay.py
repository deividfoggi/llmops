import os
from promptflow.core import Prompty
from promptflow.core import AzureOpenAIModelConfiguration

# class based flow: https://microsoft.github.io/promptflow/how-to-guides/develop-a-flex-flow/class-based-flow.html
class OldEssay:
    def __init__(self, model_config: AzureOpenAIModelConfiguration):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompty_path = os.path.join(self.current_dir, "old_essay.prompty")
        self.model_config = model_config

    def __call__(self, essay_request: str) -> str:
        print("inputs:", essay_request)
        print("getting result...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompty_path = os.path.join(current_dir, "old_essay.prompty")
        prompty = Prompty.load(source=prompty_path)
        result = prompty(
            language=essay_request["language"],
            genre=essay_request["genre"],
            statement=essay_request["statement"],
            title=essay_request["title"],
            essay=essay_request["essay"],
            support_text=essay_request["support_text"],
            skills=essay_request["skills"]
        )
        return result