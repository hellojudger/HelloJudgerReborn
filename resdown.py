# pylint:disable = all
from urllib.request import urlopen
from typing import List, Union, Optional
from os import getcwd, mkdir
from os.path import isdir
from hjreborn.i18n import _
import os, sys
from importlib import import_module

print(_("resdown.ready"))
tsinghua = input(_("resdown.changePipMirrow"))
if tsinghua.lower() == "y":
    pip_command = "\"{}\" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {} --quiet --disable-pip-version-check"
else:
    pip_command = "\"{}\" -m pip install {} --quiet --disable-pip-version-check"
github_mirrow = input(_("resdown.changeGithubMirrow"))
if github_mirrow.lower() == "y":
    github_pre = "https://gh.api.99988866.xyz/"
else:
    github_pre = ""

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

class Module:
    name = ""
    import_name = ""

    def __init__(self, name : str, import_name : Optional[str] = None):
        self.name = name
        if import_name is None:
            import_name = self.name
        self.import_name = import_name

    def download(self):
        try:
            import_module(self.import_name)
        except (ImportError, ModuleNotFoundError):
            code = os.system(pip_command.format(sys.executable, self.name))
            if code != 0:
                return False
            try:
                import_module(self.import_name)
            except (ImportError, ModuleNotFoundError):
                return False
            return True
        else:
            return True


tasks : List[Union[Resource, Module]] = list()
tasks.append(Resource(
    github_pre + "https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h",
    "testlib_sandbox/testlib.h",
    "Testlib"
))
tasks.append(Module("psutil"))
tasks.append(Module("simplejson"))
tasks.append(Module("jsonschema"))
tasks.append(Module("click"))
tasks.append(Module("rich"))
tasks.append(Module("parse"))

done = 0
fail = 0
donef = "\033[1;32m" + _("resdown.done") + "\033[0m"
failf = "\033[1;31m" + _("resdown.fail") + "\033[0m"

for i in range(len(tasks)):
    task = tasks[i]
    print(_("resdown.task").format(id = i + 1, name = task.name), end="... ")
    if task.download():
        print(donef)
        done += 1
    else:
        print(failf)
        fail += 1

print(_("resdown.end").format(done = done, fail = fail, dos = donef, fas = failf))

print(_("resdown.pause"))
input()