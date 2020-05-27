import json
import os
import time

class DataHandler:
    def __init__(self, init_cfg):
        self.local_cfg_path = init_cfg['local_cfg_path']

    def load_cfg(self):
        # Load configuration from disk
        filepath = os.path.realpath(self.local_cfg_path)
        print('DataHandler - Loading configuration from: {}'.format(filepath))
        with open(filepath, 'r') as f:
            self.cfg = json.load(f)
        print('DataHandler - Configuration loaded successfully.')
        return self.cfg

    def store_news(self, news, params_string):
        # country=se_Wed-May-27-17:15:40-2020
        filename = params_string + '_' + '-'.join(str(time.ctime()).split()).replace(':','-') + '.json'
        print('DataHandler - Storing news into file: {}'.format(filename))
        filepath = os.path.join(os.path.realpath(self.cfg["news_path"]), filename)
        # Check that the data folder exists
        if os.path.exists(os.path.realpath(self.cfg["news_path"])):
            print('DataHandler - Storing news to filepath: {}'.format(filepath))
            with open(filepath, 'w') as f:
                json.dump(news, f)
            print('DataHandler - News stored successfully.')
            return 200
        else:
            print('DataHandler - Datapath not found: {}'.format(os.path.realpath(self.cfg["news_path"])))
            return 404

    def load_news(self, filenames):
        news = {}
        for filename in filenames:
            print('DataHandler - Loading news from: {}'.format(filename))
            news[filename] = self._load_single_news(filename)
        if len(news.keys()):
            print('DataHandler - News loaded from {} files'.format(len(news.keys())))
            return news, 200
        else:
            print('DataHandler - No news loaded successfully. Check logs to know more.')
            return {}, 404

    def load_news_files(self):
        datapath = os.path.realpath(self.cfg["news_path"])
        if os.path.exists(datapath):
            filenames = []
            for filename in os.listdir(datapath):
                filenames.append(filename)
            print('DataHandler - {} filenames found.'.format(len(filenames)))
            return filenames, 200
        else:
            print('DataHandler - Datapath not found: {}'.format(datapath))
            return [], 404

    def _load_single_news(self, filename):
        filepath = os.path.join(os.path.realpath(self.cfg["news_path"]), filename)
        if os.path.isfile(filepath):
            print('DataHandler - Loading news from path: {}'.format(filepath))
            with open(filepath, 'r') as f:
                news = json.load(f)
            return news
        else:
            print('DataHandler - The file does not exist: {}'.format(filepath))
            return []