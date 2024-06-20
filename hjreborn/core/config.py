# pylint: disable=all
import importlib

class CoreConfiguration:
    __path = "config/core.json"
    __obj = {}

    def __init__(self):
        self.__obj = importlib.import_module("hjreborn.config.core").data

    def __getattr__(self, name):
        return self.__obj.get(name)

CORE = CoreConfiguration()
