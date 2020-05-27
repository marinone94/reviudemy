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
        print('Flask - An error occurred while getting the news from the news API! Error code: ' + str(status_code))
        return jsonify(response = 'An error occurred while getting the news from the news API!'), status_code
    print('Flask - News retreived successfully from NewsAPI.')
    # get parameters in url format as it is used for the filename
    params_string = newsapi._build_url_params(params)
    # store news
    status_code = data_handler.store_news(news, params_string)
    if status_code != 200:
        print('Flask - An error occurred while storing the news! Error code: ' + str(status_code))
        return jsonify(response = 'An error occurred while storing the news!'), status_code
    print('Flask - News stored successfully.')
    return jsonify(response = news), 200

@app.route('/load_news', methods=['GET'])
def load_news():
    print('Flask - /load_news endpoint.')
    filenames = request.get_json()["filenames"] #array of filenames
    news, status_code = data_handler.load_news(filenames)
    if status_code != 200:
        print('Flask - An error occurred while loading the news! Error code: ' + str(status_code))
        return jsonify(response = 'An error occurred while loading the news!'), status_code
    print('Flask - News loaded successfully.')
    return jsonify(response = news), 200

@app.route('/load_news_files', methods=['GET'])
def load_news_files():
    print('Flask - /load_news_files endpoint.')
    news, status_code = data_handler.load_news_files()
    if status_code != 200:
        print('Flask - An error occurred while loading the news files! Error code: ' + str(status_code))
        return jsonify(response = 'An error occurred while loading the news files!'), status_code
    print('Flask - News files loaded successfully.')
    return jsonify(response = news), 200

if __name__ == '__main__':
    print('Flask - Running app.')
    app.run(debug=False, host='localhost', port=5000)