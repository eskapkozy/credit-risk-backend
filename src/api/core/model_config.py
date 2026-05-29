import os

from src.api.utils import load_config


class Model_config():

    def __init__(self):

        config_path =os.getenv("MODEL_CONFIG_PATH","configs/model_config.yaml")
        self.config = load_config(config_path)

        self.state = self.config['state']

        self.woe = self.config['woe']

        self.evaluation = self.config['evaluation']