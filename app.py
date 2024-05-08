# app.py
from flask import Flask, request, jsonify, render_template
from wiki_scraper_test import search_wikipedia  # 導入從 wiki_scraper.py 定義的函數

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/send', methods=['POST'])
def send():
    if request.is_json:
        data = request.get_json()
        user_message = data.get('message', '')
        if user_message:
            results = search_wikipedia(user_message)  # 使用用戶輸入執行搜索
            return jsonify({"response": results})
        else:
            return jsonify({"response": "沒有接收到消息！"}), 400
    return jsonify({"response": "請求不包含 JSON 數據"}), 400


if __name__ == '__main__':
    app.run(debug=True)
