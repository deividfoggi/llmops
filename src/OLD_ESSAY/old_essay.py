import os
from promptflow.core import Prompty

def get_response_old_essay(essay_eval_request):
    print("inputs:", essay_eval_request)
    print("getting result...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompty_path = os.path.join(current_dir, "old_essay.prompty")
    prompty = Prompty.load(source=prompty_path)
    result = prompty(language=essay_eval_request["language"], genre=essay_eval_request["genre"], statement=essay_eval_request["statement"], title=essay_eval_request["title"], essay=essay_eval_request["essay"], support_text=essay_eval_request["support_text"], skills=essay_eval_request["skills"])
    return result