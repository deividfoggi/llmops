from promptflow.client import PFClient
import os
import json
from dotenv import load_dotenv
load_dotenv()

def main():

    pf = PFClient()
    flow = "./src/essay.prompty"  # path to the prompty file
    data = "./evaluations/essay-test-dataset.jsonl"  # path to the data file

    # base run
    base_run = pf.run(
        flow=flow,
        data=data,
        column_mapping={
            "language": "${data.language}",
            "genre": "${data.genre}",
            "statement": "${data.statement}",
            "title": "${data.title}",
            "essay": "${data.essay}",
            "support_text": "${data.support_text}",
            "skills": "${data.skills}"
        },
        stream=True,
    )
    details = pf.get_details(base_run)
    print(details.head(10))


    # Evaluation run
    eval_prompty = "./evaluations/prompty-answer-score-eval.prompty"
    eval_run = pf.run(
        flow=eval_prompty,
        data=data,  
        run=base_run, 
        column_mapping={
            "question": "${data.question}",
            "answer": "${run.outputs.output}",
            "ground_truth": "${data.ground_truth}",
        },
        stream=True,
    )

    # https://github.com/microsoft/promptflow/discussions/3352
    print("SYSTEM_METRICS: " + json.dumps(eval_run.properties["system_metrics"], indent=2))

    details = pf.get_details(eval_run)

    print(details.head(10))

    details = pf.get_details(eval_run)
    details.to_excel("prompty-answer-score-eval.xlsx", index=False)


if __name__ == '__main__':
    import promptflow as pf
    main()