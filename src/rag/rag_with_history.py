import os
from openai import AzureOpenAI
from rag.azure_ai_search import get_doc_azure_ai
import tiktoken
import json
from rag.cosmos_db import *
import logging


# importing Azure OpenAI creds
api_key = os.environ.get("AZURE_OPENAI_KEY")
azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
deployment_name = os.environ.get("CHAT_DEPLOYMENT_NAME")
TOKEN_LIMIT = 4000

client = AzureOpenAI(
    azure_endpoint=azure_endpoint, api_key=api_key, api_version="2023-05-15"
)

system_instruction = {
    "role": "system",
    "content": """Falls am Anfang einer Nachricht ein Kontext steht, versuche die Frage des Nutzers möglichst auf Basis des Kontextes zu beantworten.
    Du bist höflich und sprichst den Nutzer immer mit 'Sie' an.""",
}

system_instruction_no_context = {
    "role": "system",
    "content": "Du bist höflich und sprichst den Nutzer immer mit 'Sie' an.",
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

def cut_tokenlength(conversation_id):    
    messages= get_chat_history(conversation_id)
    msg_json= json.dumps(messages)

    #tokenize input
    tokenizer = tiktoken.get_encoding("p50k_base")
    tokenized_input= tokenizer.encode(msg_json)
    
    #calculate tokenlength
    tokenlength=len(tokenized_input)

    #adjust tokenlength by cutting first messages from history
    if tokenlength > TOKEN_LIMIT-500:
        offset= TOKEN_LIMIT-500
        newmessages = messages[-offset:]
        return newmessages
    else:
        return messages

def generate_answer(prompt, conversation_id):
    context = "\n".join(get_doc_azure_ai(prompt, similarity_threshold=0.8))

    if context:
        # create the messages array with chathistory and context from azure ai search
        messages = cut_tokenlength(conversation_id)
        messages.insert(0, system_instruction)
        messages.append({"role": "user", "content": f"{context}\n{prompt}"})
    else:
        # create the messages array without any context
        messages = get_chat_history(conversation_id)
        messages.insert(0, system_instruction_no_context)
        messages.append({"role": "user", "content": prompt})

    logging_item = json.dumps(messages)
    start = 0
    if len(logging_item) > 200:
        start = len(logging_item) - 200
    logging.info(logging_item[start:], flush=True)

    # retrieve answer
    response = client.chat.completions.create(
        model=deployment_name,
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
