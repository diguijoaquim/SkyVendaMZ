from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from huggingface_hub import InferenceClient
import json
from pydantic import BaseModel
import requests

user_history={}

class UserMessage(BaseModel):
    message: str
    sender_id:str

def getAnswer(sender_id, question):
    # Recuperar o histórico do usuário ou criar uma lista vazia se não existir
    if sender_id in user_history:
        history = user_history[sender_id]
    else:
        history = []

    # Adicionar a nova mensagem ao histórico
    history.append({"role": "user", "content": question})
    
    # Manter o histórico no limite de 10 mensagens
    if len(history) > 10:
        history = history[-10:]

    # Adicionar o histórico ao prompt para dar contexto à IA
    messages = [
        {"role": "system", "content": data}
    ] + history

    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=messages,
        max_tokens=500
    )
    
    # Obter a resposta
    answer = completion.choices[0].message['content']

    # Adicionar a resposta da IA ao histórico
    history.append({"role": "assistant", "content": answer})

    # Salvar o histórico atualizado para esse usuário
    user_history[sender_id] = history

    resposta=json.loads(answer)
    
    if resposta["type"]=="run_request":
        ## run some request to the api
        response = requests.get(resposta["url_to_fetch"])
        resposta_api=response.json()
        if resposta_api:
            ai_response={
                "type":"with_api",
                "ai_message":resposta['if_find_items'],
                "api_data":resposta_api
            }
            return ai_response
        else:
            ai_response={
                "type":"without_api",
                "ai_message":resposta['i_not_found'],
            }

            return ai_response
        
    else:
        return resposta
    

# Configuração do cliente da API da Hugging Face
client = InferenceClient(api_key="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")
with open("data/data.txt", "r") as file:
    data = file.read()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
def read_root(message:UserMessage):
    return getAnswer(message.sender_id,message.message)


