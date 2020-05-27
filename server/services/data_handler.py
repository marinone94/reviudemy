import json

class DataHandler:
    def __init__(self, init_cfg):
        self.local_cfg_path = init_cfg['local_cfg_path']

    def load_cfg(self):
        with open(self.local_cfg_path, 'r') as f:
            self.cfg = json.load(f)
        return self.cfg