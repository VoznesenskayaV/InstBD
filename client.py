import requests
from cryptography.fernet import Fernet

def make_request():
    # Шифруем данные перед отправкой
    key = open("encryption_key.txt","rb").read()
    f = Fernet(key)
    encrypted_data = f.encrypt(b"some_data").decode()

    data = {"data": encrypted_data}

    s = requests.Session()
    s.verify = False  # отключаем проверку самоподписанного сертификата
    s.cert = ('client_cert.pem', 'client_key.pem')

    try:
        response = s.post('https://localhost:5000/api/data', json=data)
        if response.status_code == 200:
            print("Ответ сервера:", response.json())
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    make_request()

