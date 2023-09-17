import simplejson as json
from os import PathLike

class CoreConfiguration:
    __path = "config/core.json"
    __obj = {}

    def __init__(self):
        with open(self.__path, encoding="utf-8", mode="r") as f:
            self.__obj = json.load(f)

    def __getattr__(self, name):
        return self.__obj.get(name)

CORE = CoreConfiguration()
