from promptflow.core import Prompty

def get_response_old_essay(essay_eval_request):
    print("inputs:", essay_eval_request)
    print("getting result...")
    prompty = Prompty.load(source="./src/OLD_ESSAY/old_essay.prompty")
    result = prompty(language = essay_eval_request["language"], genre = essay_eval_request["genre"], statement = essay_eval_request["statement"], title = essay_eval_request["title"], essay = essay_eval_request["essay"], support_text = essay_eval_request["support_text"], skills = essay_eval_request["skills"])
    return result