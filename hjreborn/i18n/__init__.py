# pylint:disable = all
from locale import getdefaultlocale
from os import listdir
import os.path
import importlib

this_path = os.path.split(os.path.abspath(__file__))[0]

locale = getdefaultlocale()[0]
_languages = listdir(this_path)
languages = []
for i in _languages:
    if i.endswith(".py") and i != "__init__.py":
        languages.append(i.split('.')[0])
del _languages

if locale not in languages:
    locale = "en_US"

obj : dict = importlib.import_module("hjreborn.i18n.{}".format(locale)).data

def translate(content : str) -> str:
    return obj.get(content, content)

_ = translate

def switch_language(new : str):
    global locale, languages, obj
    locale = new
    if locale not in languages:
        locale = "en_US"
    obj = importlib.import_module("i18n.{}".format(locale)).data
