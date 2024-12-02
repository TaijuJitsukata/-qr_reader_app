from flask import Flask, render_template, request, jsonify
import requests
import json
import os  # 環境変数を取得するためのモジュールをインポート

app = Flask(__name__, static_folder="static", template_folder="static")

# Google Safe Browsing APIキー
API_KEY = 'AIzaSyA4AFpKB4rW-ZSHfcrk3zgs4-Fgy4KTPPI'

# URLの安全性をチェックする関数
def is_safe_url(url):
    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}'
    payload = {
        "client": {
            "clientId": "qr_reader_app",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        threat_info = response.json()
        return 'matches' not in threat_info  # matchesがなければ安全
    return False

# ホームページを提供
@app.route('/')
def index():
    return render_template('index.html')

# QRコードの内容をチェックするAPI
@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')
    is_safe = is_safe_url(url)
    return jsonify({'is_safe': is_safe})

# アプリケーションのエントリポイント
if __name__ == '__main__':
    # Render環境では動的ポートを取得する必要がある
    port = int(os.getenv("PORT", 5000))  # 環境変数PORTがない場合はデフォルトで5000を使用
    app.run(host='0.0.0.0', port=port, debug=False)  # hostを0.0.0.0に設定
