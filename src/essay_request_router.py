from dotenv import load_dotenv
load_dotenv()

from sys import argv
import os
import pathlib
from promptflow.tools.common import init_azure_openai_client
from promptflow.connections import AzureOpenAIConnection
from promptflow.core import (AzureOpenAIModelConfiguration, Prompty, tool)
from flask import Flask, request, jsonify
from OLD_ESSAY.old_essay import get_response_old_essay

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
    

    result = get_response_old_essay(essay_eval_request)

    return result

# create an api to receive a post using flask

app = Flask(__name__)

@app.route('/score', methods=['POST'])
def essay_request_router():
    essay_eval_request = request.get_json()
    response = get_response(essay_eval_request)
    return response

if __name__ == "__main__":
    app.run(port=8080, debug=True)