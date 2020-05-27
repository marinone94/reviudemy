from flask import Flask, request, jsonify
import time
import json

from services.data_handler import DataHandler
from services.newsapi import NewsAPI

# Initialize Flask app
app = Flask(__name__)
print('Flask - Creating app.')

# Load initial configuration
with open('./cfg/init_cfg.json', 'r') as f:
    init_cfg = json.load(f)

# Initialize the data handler and load the global configuration
data_handler = DataHandler(init_cfg)
cfg = data_handler.load_cfg()
# cfg = data_handler.cfg

# Initialize the news API
newsapi = NewsAPI(cfg["newsapi_url"])

# endpoints
@app.route('/test', methods=['GET'])
def test():
    print('Flask - /test endpoint.')
    msg = "App is running: " + time.ctime()
    return jsonify(response = msg)

@app.route('/get_news', methods=['GET', 'POST'])
def get_news():
    print('Flask - /get_news endpoint.')
    params = request.get_json()
    # get news
    news, status_code = newsapi.get_news(params)
    if status_code != 200:
        return jsonify(response = 'An error occurred while getting the news from the news API!'), status_code
    # # store news
    # status_code = data_handler.store(news)
    # if status_code != 200:
    #     return jsonify(response = 'An error occurred while storing the news!'), status_code
    return jsonify(response = news), 200

if __name__ == '__main__':
    print('Flask - Running app.')
    app.run(debug=False, host='localhost', port=5000)