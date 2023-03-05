import os
import json


class NeacConfigModule:
    def __init__(self, data):
        for var, val in data.items():
            self.__setattr__(var, val)

class NeacConfig:
    
    def __init__(self, configFileName='config.json'):
        configFilePath = os.path.join(os.sep.join(__file__.split(os.sep)[:-1]), "../" + configFileName)
        with open(configFilePath, 'r', encoding='utf-8') as configFile:
            for moduleName, data in json.loads(configFile.read()).items():
                self.__setattr__(moduleName, NeacConfigModule(data))
