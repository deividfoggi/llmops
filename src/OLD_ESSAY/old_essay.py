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
            lingua=essay_request["lingua"],
            genero=essay_request["genero"],
            tema=essay_request["proposta"],
            titulo=essay_request["tema"],
            redacao=essay_request["redacao"],
            material_apoio=essay_request["material_apoio"],
            skills=essay_request["skills"]
        )
        return result