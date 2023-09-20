# pylint: disable=all
from abc import ABC, abstractmethod
from core.signals import *
from i18n import _
import re

class Judger(ABC):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    @abstractmethod
    def judge(self, out : str, ans : str):
        pass


class StrictCompare(Judger):
    def judge(self, out : str, ans : str):
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
    def judge(self, out : str, ans : str):
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
    def judge(self, out : str, ans : str):
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
                    return InvalidAnswer(
                        _("core.judge.valueNotReal")
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

