# pylint:disable = all
from locale import getdefaultlocale
from os import listdir
try:
    import simplejson as json
except (ImportError, ModuleNotFoundError):
    import json

locale = getdefaultlocale()[0]
_languages = listdir("i18n/")
languages = []
for i in _languages:
    if i.endswith(".json"):
        languages.append(i.split('.')[0])
del _languages

if locale not in languages:
    locale = "en_US"

with open("i18n/{}.json".format(locale), "r", encoding="utf-8") as fp:
    obj = json.load(fp)

def translate(content : str) -> str:
    return obj.get(content, content)

_ = translate

def switch_language(new : str):
    global locale, languages, obj
    locale = new
    if locale not in languages:
        locale = "en_US"
    with open("i18n/{}.json".format(locale), "r", encoding="utf-8") as fp:
        obj = json.load(fp)
