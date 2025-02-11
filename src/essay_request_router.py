from dotenv import load_dotenv
load_dotenv()

from sys import argv
import os
import pathlib
from promptflow.tools.common import init_azure_openai_client
from promptflow.connections import AzureOpenAIConnection
from promptflow.core import (AzureOpenAIModelConfiguration, Prompty, tool)
from flask import Flask, request, jsonify
from OLD_ESSAY.old_essay import OldEssay
from POEMA_FALADO.POEMA_FALADO_1EM import EssayEvaluationFlow, EssayInput

@tool
def get_response(essay_request):
    print("inputs:", essay_request)
    print("getting result...")

    model_config = AzureOpenAIModelConfiguration(
       azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""),
       api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
       azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
       api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    )
    # override_model = {
    #     "configuration": configuration,
    #     "parameters": {"max_tokens": 512}
    # }
    
    # select the case based on the essay_type property from essay_request
    essay_type = essay_request[0]['genero']

    result = "";

    if essay_type == 'Poema Falado (Poetry Slam)':
        #result = get_response_poema_falado(essay_request,model_config)
        poema_falado = EssayEvaluationFlow(model_config)
        result = poema_falado(essay_request, "None")
    elif essay_type == 'redacao simples':
        #calling using class based flow
        old_essay = OldEssay(model_config)
        result = old_essay(essay_request[0])

    return result

# create an api to receive a post using flask

app = Flask(__name__)

@app.route('/score', methods=['POST'])
def essay_request_router():
    essay_request = request.get_json()
    response = get_response(essay_request)
    return response

if __name__ == "__main__":
   app.run(port=8080, debug=True)