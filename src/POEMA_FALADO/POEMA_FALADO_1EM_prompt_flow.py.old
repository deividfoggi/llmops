import os
from promptflow.core import Prompty

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

def get_response_poema_falado(essay_request, model_config):
    print("inputs:", essay_request)
    print("getting result...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompty_path = os.path.join(current_dir, "poema_falado.prompty")
    prompty = Prompty.load(source=prompty_path)
    result = prompty(
        lingua=essay_request["lingua"],
        tema=essay_request["tema"],
        criterios=criterium,
        genero = essay_request["genero"],
        proposta = essay_request["proposta"],
        relembre_genero = essay_request["relembre_genero"],
        titulo = essay_request["titulo"],
        redacao = essay_request["redacao"],
        response_format = "text"
    )
    return result