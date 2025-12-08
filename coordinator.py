from flask import Flask, request
import requests

app = Flask(__name__)
server_urls = ['https://127.0.0.1:5000', 'https://192.168.0.137:5000']

@app.route('/api/data', methods=['POST'])
def handle_request():
    data = request.get_json()
    for url in server_urls:
        try:
            response = requests.post(f"{url}/api/data", json=data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
    return {'error': 'All servers are down'}, 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)