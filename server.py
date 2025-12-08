from flask import Flask, request
from cryptography.fernet import Fernet

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        # Получаем зашифрованные данные из запроса
        encrypted_data = request.get_json()['data']

        # Декодируем и расшифровываем данные
        key = open('encryption_key.txt', 'rb').read()
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data.encode())

        # Можно обработать данные здесь
        print("Получено и расшифровано:", decrypted_data.decode())

        return {'result': 'ok'}
    except Exception as e:
        print("Ошибка на сервере:", e)
        return {"error": str(e)}, 500

if __name__ == '__main__':
    # Запуск HTTPS сервера на порту 5000 с самоподписанным сертификатом
    app.run(host='0.0.0.0', port=5000, ssl_context=('server_cert.pem', 'server_key.pem'))

