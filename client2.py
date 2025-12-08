import requests
from cryptography.fernet import Fernet

def make_request():
    # Шифруем данные так же, как для client.py
    key = open("encryption_key.txt", "rb").read()
    f = Fernet(key)
    encrypted_data = f.encrypt(b"some_data").decode()

    data = {"data": encrypted_data}

    s = requests.Session()
    s.verify = False  # отключаем проверку самоподписанного сертификата
    s.cert = ('client_cert.pem', 'client_key.pem')  # клиентский сертификат

    url = 'https://localhost:5000/api/data'  # теперь HTTPS, порт 5000

    try:
        response = s.post(url, json=data)
        if response.status_code == 200:
            print("Ответ сервера:", response.json())
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print("Ошибка запроса:", e)

if __name__ == "__main__":
    make_request()

