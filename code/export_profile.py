import json
import os

prompts = [
    {
        "description": "Paragrafo 1: Area di Provenienza",
        "text": "Paragrafo-1.txt"
    },
    {
        "description": "Paragrafo 2: Titolo di Studio",
        "text": "Paragrafo-2.txt"
    },
    {
        "description": "Paragrafo 3.1: Competenze Professionali (1/2)",
        "text": "Paragrafo-3.1.txt"
    },
    {
        "description": "Paragrafo 3.2: Competenze Professionali (2/2)",
        "text": "Paragrafo-3.2.txt"
    }
]


for index, prompt in enumerate(prompts):
    with open(os.path.join('prompts', 'profilo01', prompt["text"]), 'r', encoding='utf-8') as file:
        prompt_text = file.read()
        prompt['text'] = prompt_text

import json
with open('profile001.json', 'w') as f:
    json.dump(prompts, f)
