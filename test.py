import requests

# Define the URL, headers, and data for the PUT request
url = 'http://127.0.0.1:5000/produtos/sapatos-nike'
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImxvamEiLCJleHAiOjE3MzczNzc3NDZ9.nGVzluh7k3pibQW0P5ygW3WY-I5rnoQdLE5VEMKhdZU',
    'Content-Type': 'application/x-www-form-urlencoded'
}
data = {
    'estado': 'semno',
    'descricao': 'blabla',
    'preco': 2000,
    'categoria': 'vestuario',
    'tipo': 'string',
    'disponiblidade': 'string',
    'detalhes': 'string',
    'nome': 'sapto2eeee',
    'quantidade_estoque': 3
}

# Send the PUT request and get the response
response = requests.put(url, headers=headers, data=data)

# Print the status code and response text
print(response.status_code)
print(response.text)