from dotenv import load_dotenv
load_dotenv()

from sys import argv
import os
import pathlib
from promptflow.tools.common import init_azure_openai_client
from promptflow.connections import AzureOpenAIConnection
from promptflow.core import (AzureOpenAIModelConfiguration, Prompty, tool)
from flask import Flask, request, jsonify

@tool
def get_response(essay_eval_request):
    print("inputs:", essay_eval_request)
    print("getting result...")

    configuration = AzureOpenAIModelConfiguration(
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "")
    )
    # override_model = {
    #     "configuration": configuration,
    #     "parameters": {"max_tokens": 512}
    # }
    
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "./essay.prompty")
    prompty_obj = Prompty.load(data_path)

    result = prompty_obj(language = essay_eval_request["language"], genre = essay_eval_request["genre"], statement = essay_eval_request["statement"], title = essay_eval_request["title"], essay = essay_eval_request["essay"], support_text = essay_eval_request["support_text"], skills = essay_eval_request["skills"])

    print("result: ", result)

    return result

# create an api to receive a post using flask

app = Flask(__name__)

@app.route('/essay', methods=['POST'])
def essay():
    essay_eval_request = request.get_json()
    response = get_response(essay_eval_request)
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=8080, debug=True)