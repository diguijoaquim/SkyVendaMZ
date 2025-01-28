import requests

# Configurações da API
url = "https://api.africastalking.com/version1/messaging/bulk"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    #s"apiKey": "atsk_b4716771c78e659d863ad07c5292284d5501df7a3d5ec4997de3657581d8f3388203aabe"  # Substitua pela sua API Key
}

# Dados para enviar o SMS
data = {
    "username": "sandbox",  # Substitua pelo seu nome de usuário
    "message": "This is a sample message.",  # Mensagem que será enviada
    "senderId": "34904",  # ID do remetente (opcional, dependendo da configuração)
    "phoneNumbers": [
        "+258860289475",  # Números de telefone no formato internacional
        "+258848446324"
    ]
}

# Fazendo a requisição POST
try:
    response = requests.post(url, json=data, headers=headers)
    
    # Verificando a resposta
    if response.status_code == 200:
        print("SMS enviado com sucesso!")
        print("Resposta:", response.json())
    else:
        print("Erro ao enviar SMS:", response.status_code)
        print("Detalhes:", response.text)
except Exception as e:
    print("Erro na requisição:", str(e))