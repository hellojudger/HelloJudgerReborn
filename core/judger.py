# pylint: disable=all
from abc import ABC, abstractmethod
import xml.etree.cElementTree as cElementTree
from core.signals import *
from i18n import _
from core.run import CPP, Limits
from typing import Optional
from core.config import CORE
from os import mkdir, remove
from os.path import isdir, abspath
import shutil
from uuid import uuid4
import re

class Judger(ABC):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    @abstractmethod
    def judge(self, in_ : str, out : str, ans : str):
        pass


class StrictCompare(Judger):
    def judge(self, in_ : str, out : str, ans : str):
        out = out.splitlines()
        ans = ans.splitlines()
        if len(out) != len(ans):
            return WrongAnswer(
                _("core.judge.rowUnmatched")
                .format(arow=len(ans), orow=len(out))
            )
        for i in range(0, len(out)):
            if len(out[i]) != len(ans[i]):
                return WrongAnswer(
                    _("core.judge.columnUnmatched")
                    .format(row=i+1, acol=len(ans[i]), ocol=len(out[i]))
                )
            for j in range(0, len(out[i])):
                if out[i][j] != ans[i][j]:
                    return WrongAnswer(
                        _("core.judge.valueUnmatched")
                        .format(row=i+1, col=j+1, aval=ans[i][j], oval=out[i][j])
                    )
        return Accepted(_("core.judge.accepted").format(row=len(out)))


def wash(string : str):
    string = string.lstrip().rstrip()
    string = re.sub(r"[\ \t]+", " ", string)
    string = re.sub(r"[\r\n]+", "\n", string)
    string = string.splitlines()
    arr = []
    for i in range(len(string)):
        arr.append(string[i].split(' '))
    return arr


class RowCompare(Judger):
    def judge(self, in_ : str, out : str, ans : str):
        out = wash(out)
        ans = wash(ans)
        if(len(ans) != len(out)):
            return WrongAnswer(
                _("core.judge.rowUnmatched")
                .format(arow=len(ans), orow=len(out))
            )
        for i in range(0, len(out)):
            if len(out[i]) != len(ans[i]):
                return WrongAnswer(
                    _("core.judge.columnUnmatched")
                    .format(row=i+1, acol=len(ans[i]), ocol=len(out[i]))
                )
            for j in range(0, len(out[i])):
                if out[i][j] != ans[i][j]:
                    return WrongAnswer(
                        _("core.judge.valueUnmatched")
                        .format(row=i+1, col=j+1, aval=ans[i][j], oval=out[i][j])
                    )
        return Accepted(_("core.judge.accepted").format(row=len(out)))

class RealCompare(Judger):
    def judge(self, in_ : str, out : str, ans : str):
        out = wash(out)
        ans = wash(ans)
        eps = pow(10, -self.kwargs.get("precision", 0))
        if(len(ans) != len(out)):
            return WrongAnswer(
                _("core.judge.rowUnmatched")
                .format(arow=len(ans), orow=len(out))
            )
        for i in range(0, len(out)):
            if len(out[i]) != len(ans[i]):
                return WrongAnswer(
                    _("core.judge.columnUnmatched")
                    .format(row=i+1, acol=len(ans[i]), ocol=len(out[i]))
                )
            for j in range(0, len(out[i])):
                try:
                    x = float(out[i][j])
                except ValueError:
                    return WrongAnswer(
                        _("core.judge.valueNotReal")
                        .format(row=i+1, col=j+1, value=out[i][j])
                    )
                try:
                    y = float(ans[i][j])
                except ValueError:
                    return JudgeFailed(
                        _("core.judge.answerValueNotReal")
                        .format(row=i+1, col=j+1, value=ans[i][j])
                    )
                if abs(x - y) > eps:
                    return WrongAnswer(
                        _("core.judge.realUnmatched")
                        .format(row=i+1, col=j+1, aval=ans[i][j], oval=out[i][j],
                            diff=("{:." + str(self.kwargs.get("precision", 0)) + "f}").format(float(abs(x-y)))
                        )
                    )
        return Accepted(_("core.judge.accepted").format(row=len(out)))

class TestlibJudger(Judger):
    def judge(self, in_ : str, out : str, ans : str):
        spj : Optional[str] = self.kwargs.get("path")
        if spj is None:
            return RowCompare().judge(in_, out, ans)
        spj = abspath(spj)
        if not isdir(CORE.testlib_sandbox):
            mkdir(CORE.testlib_sandbox)
        uuid = str(uuid4())
        shutil.copyfile(spj, abspath("{}/{}.exe".format(CORE.testlib_sandbox, uuid)))
        spj = abspath("{}/{}.exe".format(CORE.testlib_sandbox, uuid))
        inf = abspath("{}/{}.in".format(CORE.testlib_sandbox, uuid))
        ouf = abspath("{}/{}.out".format(CORE.testlib_sandbox, uuid))
        ansf = abspath("{}/{}.ans".format(CORE.testlib_sandbox, uuid))
        resf = abspath("{}/{}.xml".format(CORE.testlib_sandbox, uuid))
        with open(inf, "w", encoding="utf-8") as f:
            f.write(in_)
        with open(ouf, "w", encoding="utf-8") as f:
            f.write(out)
        with open(ansf, "w", encoding="utf-8") as f:
            f.write(ans)
        sig = CPP.run_interpret(
            "{} \"{}\" \"{}\" \"{}\" \"{}\" -appes".format(spj, inf, ouf, ansf, resf), 
            Limits(CORE.spj_time_limit, CORE.spj_memory_limit)
        )
        tree = cElementTree.parse(resf)
        remove(spj);remove(inf);remove(ouf);remove(ansf);remove(resf)
        outcome = tree.getroot().attrib["outcome"]
        code = 0
        if sig == ProgramRuntimeError():
            code = sig.code
        text = tree.getroot().text
        if text is None:
            text = ""
        message = outcome + " " + text
        if code == 0:
            return Accepted(message)
        elif outcome == "points" and code < 16:
            points = float(tree.getroot().attrib["points"])
            obj = PartiallyCorrect(message)
            obj.partially = points
            obj.is_points = False
            return obj
        elif code in [1, 2, 4]:
            return WrongAnswer(message)
        elif code >= 16:
            points = code - 16
            obj = PartiallyCorrect(message)
            obj.points = points
            obj.is_points = True
            return obj
        else:
            return JudgeFailed(message)
