import requests

def verify_payment():
    url = "https://api.paychangu.com/verify-payment/2345"
    headers = {
        "Authorization": "Bearer SEC-TEST-TXufbColCgWYrhZPvABr1jIK6djgMFB7",
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    # Exibir o status da resposta e os dados retornados
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)

if __name__ == "__main__":
    verify_payment()
