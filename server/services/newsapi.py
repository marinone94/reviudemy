import requests
import os

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, api_key):
        self.api_key = api_key
    def __call__(self, r):
        r.headers["authorization"] = "Bearer {}".format(self.api_key)
        return r

class NewsAPI:
    def __init__(self, newsapi_url):
        self.newsapi_url = newsapi_url
        
    def get_news(self, params):
        print('NewsAPI - Getting headlines. Parameters: {}'.format(params))
        news, status_code = self._get_top_headlines(params)
        if status_code != 200:
            print('NewsAPI - An error occurred while getting the news from the news API! Error code: {}'.format(status_code))
            return {}, status_code
        print('NewsAPI - {} news articles retreived.'.format(len(news)))
        return news, 200

    def _get_top_headlines(self, params):
        url = self.newsapi_url + self._build_url_params(params)
        print('NewsAPI - Getting news from the news API. URL: {}'.format(url))
        api_key = os.environ.get("K8S_SECRET_NEWSAPI_KEY")
        response = requests.get(url, auth=BearerAuth(api_key))
        if response.status_code != 200:
            return {}, response.status_code
        return response.json()["articles"], 200

    def _build_url_params(self, params):
        str_params = ""
        for key in params:
            str_params += key + "=" +params[key] + "&"
        return str_params[:-1]
