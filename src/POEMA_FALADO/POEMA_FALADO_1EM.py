# az login --tenant 16b87798-4517-442c-9200-ce1cca93259c
import os
import json
import re
from typing import List, Dict, Optional, TypedDict

from dotenv import load_dotenv, find_dotenv
import time
import tiktoken
import yaml

import pandas as pd
from promptflow.core import Prompty, AzureOpenAIModelConfiguration
from promptflow.tracing import trace
from promptflow.evals.evaluate import evaluate
from promptflow.evals.evaluators import (
    RelevanceEvaluator,
    CoherenceEvaluator
)

start_time = time.time()
load_dotenv(find_dotenv())
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#BASE_DIR = r'C:\Users\guilherme.julio\PYTHON_VSCODE\essay_evaluation_flow\1EM_1BIM_POEMA_FALADO'
SAVE_NAME = 'teste_unico.json'
PROMPT_NAME = 'poema_falado.prompty'
READ_NAME = 'anulacao_poema_falado_1bim_1EM.json'


# config_4o_mini = AzureOpenAIModelConfiguration(
#     azure_deployment="seducsp",#"playground-4o",
#     azure_endpoint=os.getenv("GPT_4OMINI_URL"),
#     api_version="2024-08-01-preview",#"2024-02-15-preview", 
#     api_key=os.getenv("AZURE_OPENAI_API_KEY")
# )

# config_4o_mini = AzureOpenAIModelConfiguration(
#     azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""),
#     api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
# )


EssayInput = TypedDict(
    "EssayInput",
    {
        "tema": str,
        "lingua": str,
        "genero": str,
        "proposta": str,
        "relembre_genero": str,
        "titulo": str,
        "texto": str
    }
)

Criterios = TypedDict(
    "Criteria",
    {
        "cd_habilidade": str,
        "criterio": str,
        "descricao": str
    }
)

CriteriaOutput = TypedDict(
    "Resultado",
    {
        "cd_habilidade": str,
        "descricao": str,
        "nota": float,
        "justificativa": str,
        "prompt_tokens": int,
        "completion_tokens": int
    }
)

EssayOutput = TypedDict(
    "EssayOutput",
    {
        "titulo": str,
        "criterios": List[CriteriaOutput]
    }
)


criterium = [
        {
        "cd_habilidade": 0,
        "criterio": "Anulação",
        "descricao": """
        Identifique se o texto se enquadra em alguma das situações abaixo:
        1. Se a redação foge completamente ao tema “O lugar de onde eu falo”. Não há menção nem sequer aos assuntos “lugar” ou “identidade” ou “pertencimento”. ;
        2. Se a redação não apresenta quaisquer indícios que a caracterizem como um poema, sendo representativa de outro gênero textual.
        3. Se há presença de trecho completamente desconectado do todo textual.
        
        Caso seja identificado algum dos três casos acima, você deve informar como retorno de nota:
        'SIM', e no comentário [explicando em qual dos casos acima o texto foi identificado]"
        Caso não seja identificado nenhum dos casos acima, você deve informar como retorno de nota:
        'NÃO', e a frase "Não foi identificado nehum motivo para anulação do texto." no comentário.
         """

    },
    {
        "cd_habilidade": 1,
        "criterio": "Adequção ao tema",
        "descricao": """
        A proposta de redação é: {{proposta}}
        O tema da redação é: {{tema}} 
        
        Atribua as notas de acordo com a gradação de notas abaixo: 
            2.5: a redação tangencia o tema ao abordar o assunto identidade e pertencimento, mas sem cumprir nenhuma das três tarefas solicitadas no enunciado. Ou seja, não menciona o lugar (em sentido literal ou figurado) de onde fala o eu lírico, nem explicita a relação entre esse lugar e a identidade do eu lírico, nem declara em que medida o eu lírico se sente pertencente ou não ao lugar ao qual se refere.
            5.0: a redação atende minimamente ao tema ao mencionar o lugar (em sentido literal ou figurado) de onde fala o eu lírico ou explicitar a relação entre esse lugar e a identidade do eu lírico ou declarar em que medida o eu lírico se sente pertencente ou não ao lugar ao qual se refere. Ou seja, apenas uma das três tarefas solicitadas no enunciado é cumprida. 
            7.5: a redação atende parcialmente ao tema ao cumprir ao menos duas das três tarefas solicitadas no enunciado. 
            10,0: a redação atende plenamente ao tema ao deixar claro qual é o lugar (em sentido literal ou figurado) do eu lírico, explicitar a relação entre esse lugar e a identidade do eu lírico e declarar em que medida o eu lírico se sente pertencente ou não ao lugar ao qual se refere. Ou seja, as três tarefas solicitadas no enunciado são cumpridas. 
        """

    },
    {
        "cd_habilidade": 2,
        "criterio": "Adequação ao gênero",
        "descricao": """ 
        O genero da redação é {{genero}}.
        As orientações sobre o gênero são: {{relembre_genero}}
        
        Atribua as notas de acordo com a gradação de notas abaixo: 
            2.5: o poema está escrito em versos metrificados (não livres) e não explora os sons das palavras, resultando em ausência de ritmo (ou seja, não há pausas regulares nem variações sonoras) E Não há figuras de linguagem. 
            5.0: o poema apresenta versos livres, mas ainda não explora os sons das palavras, resultando em ausência de ritmo. As figuras de linguagem estão presentes, mas de maneira pontual (apenas em trechos localizados da redação).
            7.5: o poema apresenta versos livres e explora os sons das palavras de forma adequada, ou seja, cria um ritmo perceptível. Além disso, a maior parte das estrofes é composta por figuras de linguagem.
            10.0: o gênero está devidamente configurado. O poema apresenta versos livres, explora os sons das palavras de forma a criar um ritmo perceptível, que pode se construir por meio de repetições sonoras ou variações de tonicidade, E utiliza figuras de linguagem em todas as estrofes.
        """
    },
    {
        "cd_habilidade": 3,
        "criterio": "Coerencia",
        "descricao": """
        As construções linguísticas incomuns (desvios de ortografia e sintaxe) nos poemas são intencionais e fazem parte de sua estética, logo não devem ser avaliadas como desvio.
        
        Atribua as notas de acordo com a gradação de notas abaixo:
            0.0: não há quaisquer tentativas de estabelecer relações lógicas entre as ideias; a redação é totalmente incoerente.
            2.5: há tentativa de estabelecer relações lógicas entre as ideias, mas há contradições graves e não intencionais, ou seja, que não fazem sentido no todo da redação.
            5.0: a redação é minimamente coerente; as ideias são apresentadas em uma sequência lógica, com falhas pontuais, como algumas ideias secundárias que não se ligam às principais E Não há contradições não intencionais.
            7.5: a redação é majoritariamente coerente; as ideias são predominantemente apresentadas em uma sequência lógica, com raras falhas, como uma ou duas ideias secundárias que não se ligam às principais E Não há contradições não intencionais.
            10.0: a redação é totalmente coerente; as ideias são apresentadas em uma sequência lógica, sem falhas nessa elaboração. Contradições, se existem, são intencionais, como, por exemplo, o trabalho com paradoxos. 
        """
    },
    {
        "cd_habilidade": 4,
        "criterio": "Coesão",
        "descricao": """
        As construções linguísticas incomuns (desvios de ortografia e sintaxe) nos poemas são intencionais e fazem parte de sua estética, logo não devem ser avaliadas como desvio.
        
        Atribua as notas de acordo com a gradação de notas abaixo:                    
            0.0: não há quaisquer indícios de coesão sequencial E/OU referencial E/OU lexical.
            2.5: recorrentes problemas de coesão sequencial E/OU referencial E/OU lexical. O texto apresenta tentativas de conectar as palavras umas às outras, mas o faz de maneira ainda muito precária.
            5.0: alguns problemas de coesão sequencial E/OU referencial E/OU lexical. Os recursos coesivos são utilizados no interior das estrofes e entre elas de forma majoritariamente adequada, mas os problemas identificados comprometem localmente a coesão.
            7.5: raros problemas de coesão sequencial E/OU referencial E/OU lexical. Os recursos coesivos são utilizados no interior das estrofes e entre elas de forma majoritariamente adequada.
            10.0: não há  problemas de coesão sequencial E/OU referencial E/OU lexical. Os recursos coesivos são utilizados no interior das estrofes e entre elas de forma totalmente adequada.
        """
    },
    {
        "cd_habilidade": 5,
        "criterio": "Convenções da escrita",
        "descricao": """
        Desconsidere desvios de ortografia, sintaxe, concordâcia e gramática que fazem parte da estética do poema.
        
        Atribua as notas de acordo com a gradação de notas abaixo:
            0.0: não há quaisquer indícios de domínio das convenções de escrita adequadas à situação comunicativa, como inventividade, conotação e marcas de oralidade e informalidade. 
            2.5: há presença de traços pontuais (características aparecem de forma isolada, sem impactar a redação como um todo) de inventividade, conotação ou marcas da oralidade. A linguagem é predominantemente rígida, estando pouco adequada à situação comunicativa.
            5.0: é detectável um esforço na construção de uma linguagem conotativa, com algumas marcas de e informalidade. Contudo, essas características são exploradas de forma inconsistente.
            7.5: a redação apresenta uma linguagem majoritariamente inventiva e conotativa, com marcas perceptíveis de oralidade e informalidade.
            10.0: a redação demonstra pleno domínio das convenções adequadas à situação comunicativa. A linguagem é altamente inventiva e conotativa, com marcas claras de oralidade e informalidade. 
        """
    }
]


class EssayEvaluationFlow:
    """
    Realiza a avaliação das redações.
    """

    def __init__(
        self,
        model_config: AzureOpenAIModelConfiguration, #configuração do modelo
        criteria: Optional[List[Dict]] = None #critérios de avaliação
    ):
        """

        """
        if criteria is None:
            criteria = criterium
        self.model_config = model_config
        self.criteria = criteria

    def __call__(
            self,
            #essay_input: List[EssayInput], #entrada de redações
            essay_input: EssayInput, #entrada da redação
            criteria_list: Criterios #lista de critérios
        ) -> EssayOutput:
        """

        """
        def calcular_tokens(texto, modelo="gpt-4o"):
            tokenizador = tiktoken.encoding_for_model(modelo)
            tokens = tokenizador.encode(texto)
            return len(tokens)
        
        responses = []
        for texto in essay_input:
            response = [self.evaluate(texto,str(criteria)) for criteria in criteria_list]
            responses.append(response)
        return responses

    @trace #usado para rastrear a execução do código
    #método que chama os inputs + critérios e envia para o prompty
    def evaluate(
        self,
        essay_input: EssayInput,
        criteria: str
    ) -> EssayOutput:
        """
        """
        #carrega o arquivo prompty
        #prompty = Prompty.load(
        #    source=f"{BASE_DIR}/{PROMPT_NAME}",
        #    model={"configuration": self.model_config},
        #)

        prompty = Prompty.load(source=f"{BASE_DIR}/{PROMPT_NAME}")
        
        #chamada que envia os parâmetros para o prompty
        output = prompty(
            lingua=essay_input["lingua"],
            tema=essay_input["tema"],
            criterios=criteria,
            genero = essay_input["genero"],
            proposta = essay_input["proposta"],
            relembre_genero = essay_input["relembre_genero"],
            titulo = essay_input["titulo"],
            redacao = essay_input["redacao"],
            response_format = "text"
        )
        
        #(trecho de código que exibe o prompt que será enviado para o modelo/)
        prompt = {
            "tema": essay_input["tema"],
            "lingua": essay_input["lingua"],
            "criterios": criteria,
            "genero": essay_input["genero"],
            "proposta": essay_input["proposta"],
            "relembre_genero": essay_input["relembre_genero"],
            "titulo": essay_input["titulo"],
            "redacao": essay_input["redacao"],
            "response_format": "text"
        }
        
        with open(f"{BASE_DIR}/{PROMPT_NAME}", "r", encoding="utf-8") as f:
            prompty_content = f.read()
            for key, value in prompt.items():
                prompty_content = prompty_content.replace(f"{{{{{key}}}}}", str(value))
                
        def calcular_tokens(texto, modelo="gpt-4o"):
            tokenizador = tiktoken.encoding_for_model(modelo)
            tokens = tokenizador.encode(str(texto))
            return len(tokens)
        
        completion_soma = calcular_tokens(output)
                
        #print(50*"--")
        #print("Prompt com as substituições:\n", prompty_content)
        #(\trecho de código que exibe o prompt que será enviado para o modelo)

        #Chamada enviado parâmetros do dicionário prompt para o arquivo prompty
        #Armazendando a chamada no dicionário "resposta"
        #resposta = prompty(**prompt)

        #declarada aqui pois houve uma condição onde a linha 289 nunca foi executada
        justificativa_anulacao = ''
        
        #Precisamos criar a regra de susbstituição da justificativa quando a redação for anulada p/ todos os critérios
        #Excluindo justificativa "de_um_passo_alem" para notas >= 1.5
        for avaliacao in output.get("avaliacao", []):
            cd_habilidade = avaliacao.get("cd_habilidade", 0)
            nota = avaliacao.get("nota", "0")
            # comentando pois houve uma condição nos testes onde esse trecho nunca foi executado
            #global justificativa_anulacao
            anulacao_frase = "Redação anulada. "
            comment_1 = "Onde você está: "
            comment_2 = "Dê um passo além: "
            
            #Restrições para tratar os casos de anulação
            if cd_habilidade == 0 and nota == "SIM":
                justificativa = avaliacao.get("justificativa", {})
                justificativa_anulacao = justificativa.get("onde_voce_esta", {})#justificativa_anulação é uma lista de strings
                #print(justificativa_anulacao)
                #break #para o comando for
            elif cd_habilidade == 0 and nota == "NÃO":
                justificativa_anulacao = None
        
        #Substituição da justificativa quando a redação for anulada p/ todos os critérios
        if justificativa_anulacao:
            for avaliacao in output.get("avaliacao", []):
                nota = avaliacao.get("nota", "0")
                cd_habilidade = avaliacao.get("cd_habilidade", 0)
                justificativa = avaliacao.get("justificativa", {})
                if cd_habilidade != 0:
                    avaliacao["nota"] = 0.0
                    justificativa["onde_voce_esta"] = anulacao_frase + str(justificativa_anulacao[0])
                    if "de_um_passo_alem" in justificativa:
                        del justificativa["de_um_passo_alem"]
                    #print(avaliacao)
                
                    
        #Restrições para nota = 10.0
        for avaliacao in output.get("avaliacao", []):
            cd_habilidade = avaliacao.get("cd_habilidade", 0)
            if cd_habilidade != 0:
                nota = avaliacao.get("nota", "0")
                try:
                    if float(nota) == 10.0:
                        justificativa = avaliacao.get("justificativa", {})
                        if "de_um_passo_alem" in justificativa:
                            del justificativa["de_um_passo_alem"]
                except ValueError:
                    pass #Ignora valores não numéricos   
                
        #Aqui ele insere as frases "Onde você está" e "Dê um passo além"
        #Além de formatar em tópicos cada sugestão em dê um passo além
        for avaliacao in output.get("avaliacao", []):
            justificativa = avaliacao.get("justificativa", {})
            justificativa_esta = justificativa.get("onde_voce_esta", {}) 
            if isinstance(justificativa_esta, str):
                formatacao_1 = comment_1 + "\n" + f"- {justificativa_esta}"
                justificativa["onde_voce_esta"] = [formatacao_1]
            elif isinstance(justificativa_esta, list):
                formatacao_1 = comment_1 + "\n" + "\n".join(f"- {item}" for item in justificativa_esta)
                justificativa["onde_voce_esta"] = [formatacao_1]
                
            # Primeiro precisa verificiar se a chave "de_um_passo_alem" existe
            # Porque nos casos de anulação, a chave "de_um_passo_alem" é deletada por isso (else: pass)
            if "de_um_passo_alem" in justificativa:
                justificativa_alem = justificativa.get("de_um_passo_alem", {})
                if isinstance(justificativa_alem, str):
                    formatacao_2 = comment_2 + "\n" + f"- {justificativa_alem}"
                    justificativa["de_um_passo_alem"] = [formatacao_1]
                elif isinstance(justificativa_alem, list):
                    formatacao_2 = comment_2 + "\n" + "\n".join(f"- {item}" for item in justificativa_alem)
                    justificativa["de_um_passo_alem"] = [formatacao_2]
            else:
                pass       
               
        modified_output = json.dumps(output, ensure_ascii=False, indent=2)
        with open(f'{BASE_DIR}/{SAVE_NAME}', 'w', encoding='utf-8') as file:
            file.write(modified_output)

#        print("JSON de resposta modificado:\n", json.dumps(output, ensure_ascii=False, indent=2))
        
        
        #Início do cálculo do número de prompt_tokens/
        #Função que calcula o número de tokens de um texto
        def calcular_tokens(texto, modelo="gpt-4o-mini"):
            tokenizador = tiktoken.encoding_for_model(modelo)
            tokens = tokenizador.encode(texto)
            return len(tokens)
        
        #Dicionário com as chaves a serem substituídas no arquivo prompty
        substituir = {
            "{{criterios}}": "",
            "{{lingua}}": "",
            "{{tema}}": "",
            "{{genero}}": "",
            "{{proposta}}": "",
            "{{relembre_genero}}": "",
            "{{titulo}}": "",
            "{{redacao}}": ""
        }
        
        #Substituição das chaves no arquivo prompty
        padrao = re.compile("|".join(map(re.escape, substituir.keys())))
        
        def trocar(match):
            return substituir[match.group(0)]

        with open(f"{BASE_DIR}/{PROMPT_NAME}", "r", encoding="utf-8") as f:
            prompty_content = f.read()
            idx_system = prompty_content.find("system:")
            system_part = prompty_content[idx_system:]
            system_part = padrao.sub(trocar, system_part)
            tokens_prompty = calcular_tokens(system_part)
            #print(tokens_prompty)
            
            lingua_str = essay_input["lingua"]
            tema_str = essay_input["tema"]
            genero_str = essay_input["genero"]
            proposta_str = essay_input["proposta"]
            relembre_genero_str = essay_input["relembre_genero"]
            titulo_str = essay_input["titulo"]
            redacao_str = essay_input["redacao"]
            
            # Cálculo de tokens dos critérios
            tokens_criterios = 0
            for item in criterium:
                tokens_criterios += calcular_tokens(str(item), "gpt-4o")
                #print(item)

            # Cálculo de tokens dos parâmetros do arquivo prompty
            lingua_tokens = calcular_tokens(lingua_str, "gpt-4o")
            tema_tokens = calcular_tokens(tema_str, "gpt-4o")
            genero_tokens = calcular_tokens(genero_str, "gpt-4o")
            proposta_tokens = calcular_tokens(proposta_str, "gpt-4o")
            relembre_genero_tokens = calcular_tokens(relembre_genero_str, "gpt-4o")
            titulo_tokens = calcular_tokens(titulo_str, "gpt-4o")
            texto_tokens = calcular_tokens(redacao_str, "gpt-4o")
            
            prompt_soma = lingua_tokens + tema_tokens + genero_tokens + proposta_tokens + relembre_genero_tokens + titulo_tokens + texto_tokens + tokens_criterios + tokens_prompty
            #/fim do cálculo de prompt_tokens
            
        #retorna um dicionário com título, texto, critérios corrigidos e prompt_tokens
        #alterações na correção implicam em mudanças no que receberá o parâmetro "criterios"
        print(CriteriaOutput(titulo=essay_input["titulo"], texto=essay_input["redacao"], criterios=output, prompt_tokens=prompt_soma, completion_tokens=completion_soma))
        return CriteriaOutput(titulo=essay_input["titulo"], texto=essay_input["redacao"], criterios=output, prompt_tokens=prompt_soma, completion_tokens=completion_soma)
    
    def __aggregate__(self, line_results: List[str]) -> dict:
        """

        """
        total = len(line_results)
        avg_correctness = (
            sum(int(r["correctness"]["score"]) for r in line_results) / total
        )
        return {
            "average_correctness": avg_correctness,
            "total": total,
        }


def evaluate_essay(config: AzureOpenAIModelConfiguration, criteria_list: Criterios) -> EssayOutput:
    """
    Evaluates a list of essays based on a list of criteria.

    Args:
        config (AzureOpenAIModelConfiguration): An Azure OpenAI connection configuration.
        criteria_list (Criteria): A list of Criteria for evaluation.

    Returns:
        List[EssayOutput]: _description_
    """

    #Leitura do arquivo JSON com as redações
    with open(f"{BASE_DIR}/{READ_NAME}", "r", encoding="utf-8") as f:
        essays = json.load(f)

    #Instanciação do objeto EssayEvaluationFlow
    flow = EssayEvaluationFlow(config)
    return flow(essays, criteria_list)


def run_evaluation(eval_name, dataset_path, config: AzureOpenAIModelConfiguration):
    """
    
    Args:
        eval_name (_type_): _description_
        dataset_path (_type_): _description_
        config (_type_): _description_

    Returns:
        _type_: _description_
    """

    output_path = "./eval_results.jsonl"

    with open(f"{BASE_DIR}/{READ_NAME}", "r", encoding="utf-8") as f:
        essays = json.load(f)

    flow = EssayEvaluationFlow(config)

    #inference = flow(essays, criterium)
    relevance = RelevanceEvaluator(config)
    coherence = CoherenceEvaluator(config)

    result = evaluate(
        target=flow,
        evaluation_name=eval_name,
        data=dataset_path,
        evaluators={
            "relevance": relevance,
            "coherence": coherence
        },
        evaluator_config={
            "relevance": {
                "essay_input": "${data.essay_input}",
                "criteria_list": "${target.criterium}"
            },
            "coherence": {
                "essay_input": "${data.essay_input}",
                "criteria_list": "${target.criterium}"
            }
        },
        azure_ai_project={
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.getenv("AZURE_RESOURCE_GROUP"),
            "project_name": os.getenv("AZUREAI_PROJECT_NAME"),
        }
    )

    tabular_result = pd.DataFrame(result.get("rows"))
    tabular_result.to_json(output_path, orient="records", lines=True)

    return result, tabular_result


if __name__ == "__main__":

    #inference_4 = evaluate_essay(config_4, criterium)
    #print(inference_4)

    #inference_4o = evaluate_essay(config_4o, criterium)
    #print(inference_4o)
    #with open('teste_3B_4o_.json', 'w+', encoding='utf-8') as file:
    #    file.write(json.dumps(inference_4o, ensure_ascii=False))

    config_4o_mini = AzureOpenAIModelConfiguration(
       azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""),
       api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
       azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
       api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    )

    inference_mini = evaluate_essay(config_4o_mini, criterium)
    #print(inference_mini)
    with open(f'{BASE_DIR}/{SAVE_NAME}', 'w+', encoding='utf-8') as file:
        file.write(json.dumps(inference_mini, ensure_ascii=False))
        
    #result_4, tabular_result_4 = run_evaluation(
    #    "essay_evaluation",
    #    f"{BASE_DIR}\\redacoes.jsonl",
    #    config_4
    #)

    #result_4o, tabular_result_4o = run_evaluation(
    #    "essay_evaluation",
    #    f"{BASE_DIR}\\teste_redacao_1.jsonl",
    #    config_4o
    #)

    #result_mini, tabular_result_mini = run_evaluation(
    #    "essay_evaluation",
    #    f"{BASE_DIR}\\teste_redacao_1.jsonl",
    #    config_4o_mini
    #)

    #print(result_4o)
    #print(tabular_result_4o)
    #print(result_4o)
    #print(tabular_result_4o)

total_time = time.time() - start_time
print(total_time)