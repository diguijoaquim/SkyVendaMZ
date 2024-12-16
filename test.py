import requests

def enviar_sms(numero: str, mensagem: str) -> dict:
    """
    Envia uma mensagem SMS para um número de telefone de Moçambique usando o serviço Textbelt.

    Args:
        numero (str): Número de telefone no formato completo (+258XXXXXXX).
        mensagem (str): Texto da mensagem a ser enviada.

    Returns:
        dict: Resposta da API Textbelt.
    """
    # Verifica se o número começa com +258 (Moçambique)
    if not numero.startswith("+258"):
        raise ValueError("O número deve estar no formato completo, começando com '+258'.")

    # Token da API Textbelt
    api_key = "947d8826cee86570e8d0dbd6c312be5fa388630ccKWjtHrwtvi9ZEN7azlYQEq3G"

    # URL da API Textbelt
    url = "https://textbelt.com/text"

    # Parâmetros da requisição
    data = {
        "phone": numero,
        "message": mensagem,
        "key": api_key,
    }

    # Enviar a requisição POST para a API Textbelt
    response = requests.post(url, data=data)

    # Retornar o JSON da resposta
    return response.json()

# Exemplo de uso
if __name__ == "__main__":
    numero_destino = "+258841041035"  # Substitua pelo número de destino
    mensagem = "Seu código de confirmação é 123456."
    resposta = enviar_sms(numero_destino, mensagem)

    if resposta.get("success"):
        print("SMS enviado com sucesso!")
        print(f"Quota restante: {resposta.get('quotaRemaining')}")
    else:
        print("Falha ao enviar SMS.")
        print(resposta)

