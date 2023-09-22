# pylint:disable = all
from urllib.request import urlopen
from typing import List
from os import getcwd, mkdir
from os.path import isdir
from i18n import _

print(_("resdown.ready"))

DOWNLOAD_TIMEOUT = 10

class Resource:
    url = ""
    path = ""
    name = ""
    
    def __init__(self, url : str, path : str, name : str):
        self.url = url
        self.path = path
        self.name = name
    
    def download(self) -> bool:
        try:
            now = getcwd()
            for i in self.path.split('/')[:-1]:
                now = now + "/" + i
                if not isdir(now):
                    mkdir(now)
            data = urlopen(self.url, timeout = DOWNLOAD_TIMEOUT)
            with open(self.path, "wb") as f:
                f.write(data.read())
        except Exception:
            return False
        else:
            return True
    
tasks : List[Resource] = list()
tasks.append(Resource(
    "https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h",
    "testlib_sandbox/testlib.h",
    "Testlib"
))

done = 0
fail = 0

for i in range(len(tasks)):
    task = tasks[i]
    print(_("resdown.task").format(id = i + 1, name = task.name), end="... ")
    if task.download():
        print(_("resdown.done"))
        done += 1
    else:
        print(_("resdown.fail"))
        fail += 1

print(_("resdown.end").format(done = done, fail = fail))

print(_("resdown.pause"))
input()