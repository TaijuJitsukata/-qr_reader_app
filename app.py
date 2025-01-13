from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/check_url": {"origins": "*"}})

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
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    headers = {'Content-Type': 'application/json'}

    try:
        # APIにリクエストを送信
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # HTTPエラーをキャッチ
        result = response.json()

        # matchesがあれば危険なURLと判断
        if 'matches' in result:
            threats = []
            for match in result['matches']:
                threats.append(match['threatType'])
            return {"is_safe": False, "message": "危険なURLです。", "reasons": threats}
        
        return {"is_safe": True, "message": "安全なURLです。", "reasons": []}

    except requests.exceptions.HTTPError as e:
        # HTTPエラーの詳細を理由として返す
        return {"is_safe": None, "message": "Google Safe Browsing APIエラー", "reasons": [str(e)]}

    except requests.exceptions.RequestException as e:
        # リクエスト失敗時のエラーメッセージを返す
        return {"is_safe": None, "message": "ネットワークエラー", "reasons": [str(e)]}

    except Exception as e:
        # その他の例外処理
        return {"is_safe": None, "message": "予期しないエラーが発生しました。", "reasons": [str(e)]}

# ホームページを提供
@app.route('/')
def index():
    return render_template('index.html')

# QRコードの内容をチェックするAPI
@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')
    result = is_safe_url(url)

    return jsonify({
        'is_safe': result["is_safe"],
        'message': result["message"],
        'reasons': result["reasons"]
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
