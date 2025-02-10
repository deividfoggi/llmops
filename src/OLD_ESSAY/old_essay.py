import os
from promptflow.core import Prompty

def get_response_old_essay(essay_request, model_config):
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