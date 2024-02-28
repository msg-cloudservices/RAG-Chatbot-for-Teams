import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure_ai_search import get_doc_azure_ai
import tiktoken
import json
from cosmos_db import *
import logging


load_dotenv()


# importing Azure OpenAI creds
api_key = os.getenv("AZURE_OPENAI_KEY")
os.environ["OPENAI_API_KEY"] = api_key
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = "gpt"
TOKEN_LIMIT = 4000

client = AzureOpenAI(
    azure_endpoint=azure_endpoint, api_key=api_key, api_version="2023-05-15"
)

system_intstruction = {
    "role": "system",
    "content": "Am Anfang jeder Nachricht steht ein Kontext, den du verwendest, um deine Antworten zu erstellen. Dieser Kontext ist ein Auszug aus Dokumente, die Prozesse und Abläufe des NDR beschreiben. Du beantwortest hauptsächlich Fragen zu Abläufen von Prozessen mit Hilfe dieser Kontexte.",
}


def compute_tokens(messages):
    tokenizer = tiktoken.get_encoding("p50k_base")
    result = TOKEN_LIMIT - len(tokenizer.encode(json.dumps(messages)))
    if result < 0:
        return 0
    else:
        return result

        
def get_chat_history(conversation_id):
    message_history = query_items(conversation_id)
    sorted_message_history = sorted(
        message_history, key=lambda message: int(message["position"])
    )
    return [
        {"role": message["role"], "content": message["content"]}
        for message in sorted_message_history
    ]


def generate_answer(prompt, conversation_id):
    # create the messages array with chathistory and context from azure ai search
    messages = get_chat_history(conversation_id)
    messages.insert(0, system_intstruction)
    context = "\n".join(get_doc_azure_ai(prompt))
    print(f"context: {context}")
    messages.append({"role": "user", "content": f"{context}\n{prompt}"})

    # retrieve answer
    response = client.chat.completions.create(
        model="gpt",
        messages=messages,
        temperature=0.7,
        max_tokens=compute_tokens(messages),
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
    )
    answer = (response.choices[0].message.content).strip()
    logging.info(f"Answer: {answer}")
    if answer:
        create_items(
            {
                "conversation_id": conversation_id,
                "role": "user",
                "content": prompt,
                "position": len(messages) - 1,
            },
        )
        create_items(
            {
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": answer,
                "position": len(messages),
            },
        )

    return answer