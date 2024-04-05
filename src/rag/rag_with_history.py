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
TOKEN_LIMIT = int(os.environ.get("TOKEN_LIMIT", 16000))
ANSWER_TOKENS = int(os.environ.get("ANSWER_TOKENS", 1000))

client = AzureOpenAI(
    azure_endpoint=azure_endpoint, api_key=api_key, api_version="2023-05-15"
)

system_instruction = {
    "role": "system",
    "content": """Falls am Anfang einer Nachricht ein Kontext steht, versuche die Frage der Nutzenden möglichst auf Basis des Kontextes zu beantworten.
    Du bist höflich und sprichst die User:innen immer mit 'Sie' an.""",
}

system_instruction_no_context = {
    "role": "system",
    "content": "Du bist höflich und sprichst die User:innen immer mit 'Sie' an.",
}


def compute_tokens(messages):
    tokenizer = tiktoken.get_encoding("p50k_base")
    sum_tokens = 0
    for msg in messages:
        sum_tokens += len(tokenizer.encode(msg["content"]))
    result = TOKEN_LIMIT - sum_tokens
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


def cut_tokenlength(messages):
    # tokenize input
    tokenizer = tiktoken.get_encoding("p50k_base")
    tokenized_messages = [
        len(tokenizer.encode(message["content"])) for message in messages
    ]

    # calculate tokenlength
    tokenlength = sum(tokenized_messages)

    logging.info(f"Total number of tokens: {tokenlength}")

    # adjust tokenlength by cutting first messages from history
    token_count = 0
    for message_length in tokenized_messages:
        if tokenlength - token_count <= TOKEN_LIMIT - ANSWER_TOKENS:
            return messages
        token_count += message_length
        messages.pop(0)
    return messages


def generate_answer(prompt, conversation_id):
    # retrieve documents from azure AI
    context = "\n".join(get_doc_azure_ai(prompt, similarity_threshold=0.8))

    # retrieve chat history and remove any messages exceeding the token limit
    messages = get_chat_history(conversation_id)
    messages = cut_tokenlength(messages)

    # construct messages array with system message, history and prompt
    if context:
        prompt = f"{context}\n{prompt}"
        messages.insert(0, system_instruction)
    else:
        messages.insert(0, system_instruction_no_context)
    messages.append({"role": "user", "content": prompt})

    logging_item = json.dumps(messages)
    start = 0
    if len(logging_item) > 200:
        start = len(logging_item) - 200
    logging.info(logging_item[start:])

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
                # "position": len(messages) - 1,
            },
        )
        create_items(
            {
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": answer,
                # "position": len(messages),
            },
        )

    return answer
