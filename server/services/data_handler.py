import json
import os
import time
import pymongo

class DataHandler:
    def __init__(self, init_cfg):
        self.local_cfg_path = init_cfg['local_cfg_path']
        self.mongodb_connection_string = init_cfg['mongodb_connection_string']
        self.db_name = init_cfg['db_name']
        self.use_mongodb = init_cfg['use_mongodb']

    # Load configuration
    def load_cfg(self):
        if self.use_mongodb:
            print('DataHandler - Loading configuration from MongoDB.')
            return self._load_cfg_from_mongodb()
        else:
            print('DataHandler - Loading configuration from disk.')
            return self._load_cfg_from_disk()

    def _load_cfg_from_mongodb(self):
        if 'localhost' not in self.mongodb_connection_string:
            self._build_connection_string()
        self.mongodb = pymongo.MongoClient(self.mongodb_connection_string)[self.db_name]
        print('DataHandler - Connection established: {}. Database name: {}'.format(self.mongodb_connection_string, self.db_name))
        mongo_cfg = self.mongodb.cfg.find_one({})
        local_cfg = self._load_cfg_from_disk()
        if mongo_cfg is None:
            print('DataHandler - No configuration found on MongoDB.')
            self.mongodb.cfg.insert_one({'cfg': self.cfg})
            print('DataHandler - Configuration successfully added to MongoDB.')
        elif mongo_cfg['cfg'] != local_cfg:
            print('DataHandler - Out of date configuration found on MongoDB.')
            self.mongodb.cfg.replace_one({'cfg': mongo_cfg['cfg']}, {'cfg': self.cfg})
            print('DataHandler - Configuration successfully updated in MongoDB.')
        else:
            print('DataHandler - Up to date configuration found on MongoDB.')
        return self.cfg

    def _build_connection_string(self):
        n = self._count_mongo_replicas()
        connection_string = "mongodb://"
        # original connection string: "mongodb://mongo-0.mongo,mongo-1.mongo:27017"
        port = self.mongodb_connection_string.split(':')[-1]
        for i in range(n):
            connection_string = connection_string + "mongo-" + str(i) + ".mongo,"
        connection_string = connection_string[:-1] + ':' + port
        print('DataHandler - New connection string: {}'.format(connection_string))
        self.mongodb_connection_string = connection_string

    def _count_mongo_replicas(self):
        with open('./tmp_manifests/deploy-mongo.yaml', 'r') as f:
            lines = f.readlines()
        for l in lines:
            if 'replicas' in l:
                return int(l.split()[-1])
        return 1

    def _load_cfg_from_disk(self):
        # Load configuration from disk
        filepath = os.path.realpath(self.local_cfg_path)
        print('DataHandler - Loading configuration from: {}'.format(filepath))
        with open(filepath, 'r') as f:
            self.cfg = json.load(f)
        print('DataHandler - Configuration loaded successfully.')
        return self.cfg

    def store_news(self, news, params_string):
        if self.use_mongodb:
            print('DataHandler - Storing news to MongoDB.')
            return self._store_news_to_mongodb(news, params_string)
        else:
            print('DataHandler - Storing news to disk.')
            return self._store_news_to_disk(news, params_string)

    def _store_news_to_mongodb(self, news, params_string):
        response = self.mongodb.news_names.insert_one({'document_name': params_string})
        if not response.acknowledged:
            print('DataHandler - Failed to store news names to MongoDB.')
            return 500
        response = self.mongodb.news.insert_one({'document_name': params_string, 'news': news})
        if response.acknowledged:
            print('DataHandler - News stored successfully to MongoDB.')
            return 200
        else:
            print('DataHandler - Failed to store news to MongoDB.')
            return 500

    def _store_news_to_disk(self, news, params_string):
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
        print('DataHandler - Loading news from the following files: {}'.format(filenames))
        if self.use_mongodb:
            print('DataHandler - Loading news from MongoDB.')
            news = self._load_news_from_mongodb(filenames)
        else:
            print('DataHandler - Loading news from disk.')
            news = self._load_news_from_disk(filenames)
        # Check that news object is not empty
        if len(news.keys()):
            print('DataHandler - News loaded from {} files'.format(len(news.keys())))
            return news, 200
        else:
            print('DataHandler - No news loaded successfully. Check logs to know more.')
            return {}, 404

    def _load_news_from_mongodb(self, filenames):
        news = {}
        for filename in filenames:
            response = self.mongodb.news.find_one({'document_name': filename})
            if response is not None:
                news[filename] = response['news']
                print('DataHandler - Document {} loaded successfully.'.format(filename))
            else:
                print('DataHandler - Document {} not found in MongoDB.'.format(filename))
        return news

    def _load_news_from_disk(self, filenames):
        news = {}
        for filename in filenames:
            print('DataHandler - Loading news from: {}'.format(filename))
            news[filename] = self._load_single_news(filename)
        return news

    def load_news_files(self):
        if self.use_mongodb:
            print('DataHandler - Loading news filenames from MongoDB.')
            return self._load_news_files_from_mongodb()
        else:
            print('DataHandler - Loading news filenames from disk.')
            return self._load_news_files_from_disk()

    def _load_news_files_from_mongodb(self):
        response = self.mongodb.news_names.find({})
        if response is not None:
            print('DataHandler - News filenames loaded from MongoDB.')
            filenames = []
            for resp in response:
                filenames.append(resp['document_name'])
            return filenames, 200
        else:
            print('DataHandler - Failed to load news filenames from MongoDB.')
            return [], 500

    def _load_news_files_from_disk(self):
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