# pylint:disable = all

from core.problem_validator import validate
from core.signals import *
import simplejson as json
from typing import List
from uuid import uuid4
import os, shutil
from core.run import ProgrammingLanguage, Limits, CPP
from core.judger import StrictCompare, RowCompare, RealCompare, TestlibJudger
from i18n import _
from threading import Thread
from copy import deepcopy
from core.config import CORE


class ValidationError(Exception):
    def __init__(self, message : str):
        self.message = message
    
    def __str__(self):
        return self.message

    def __repr__(self):
        return "ValidationError({})".format(self.message)


class Statement:

    type = ""
    name = ""
    path = ""

    def __init__(self, type : str, name : str, path : str):
        self.type = type
        self.name = name
        self.path = path


class Testcase:
    in_ = ""
    short_in = ""
    out = ""
    short_out = ""
    time = 0
    memory = 0
    subtask = 0
    mark = 0

    def __init__(self, inf : str, ouf : str, time : int, memory : int, subtask : int, mark : float, short_in : str, short_out : str):
        self.in_ = inf
        self.out = ouf
        self.time = time
        self.memory = memory
        self.subtask = subtask
        self.mark = mark
        self.short_in = short_in
        self.short_out = short_out


class Subtask:
    method = ""
    required : List[int] = []
    testcases : List[Testcase] = []

    def __init__(self, method : int, required : List[int], testcases : List[Testcase]):
        self.method = method
        self.required = required
        self.testcases = testcases

    def __repr__(self):
        return str(self.testcases)

class ProblemJudger:
    id = ""
    kwargs = {}

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.kwargs = kwargs

class Problem:

    data = {}
    path = ""

    def __init__(self, path : str):
        self.path = path
        sig = validate(path)
        if sig == ProblemFileInvalid():
            raise ValidationError(sig.message)
        with open("{}/problem.json".format(path), "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    def name(self) -> str:
        return self.data["name"]
    
    def statements(self) -> List[Statement]:
        arr = []
        for i in self.data["statements"]:
            path = "{}/resources/{}".format(self.path, i["path"])
            arr.append(Statement(i["type"], i.get("name", ""), path))
        return arr
    
    def type(self) -> str:
        return self.data["type"]
    
    def subtasks(self) -> List[Subtask]:
        arr = {}
        for i in self.data["testcases"]:
            j = deepcopy(i)
            j["in"] = "{}/data/{}".format(self.path, i["in"])
            j["out"] = "{}/data/{}".format(self.path, i["out"])
            j["subtask"] -= 1
            if j["subtask"] not in list(arr.keys()):
                arr[j["subtask"]] = []
            arr[j["subtask"]].append(Testcase(j["in"], j["out"], j["time"], j["memory"], j["subtask"], j["mark"], i["in"], i["out"]))
        ret = []
        for cnt, i in enumerate(self.data["subtasks"]):
            ret.append(Subtask(i["method"], i["required"], arr[cnt]))
        return ret

    def judger(self) -> ProblemJudger:
        data = self.data["judger"]
        if data.get("path") is not None:
            data["path"] = "{}/libraries/{}".format(self.path, data["path"])
        return ProblemJudger(**data)

COMPILE_FINISHED = 0
COMPILE_ERROR = 1
TESTLIB_COMPILE_ERROR = 2

class JudgeInfo:
    subtask = 0
    in_ = ""
    out = ""
    signal = Skipped()
    time_used = 0
    memory_used = 0
    mark = 0

    def __init__(self, subtask : int, in_ : str, out : str, signal, time_used, memory_used, mark):
        self.subtask = subtask
        self.in_ = in_
        self.out = out
        self.signal = signal
        self.time_used = time_used
        self.memory_used = memory_used
        self.mark = mark


def _slot(info : JudgeInfo):
    print(info.subtask, info.in_, info.out, info.signal, info.time_used, info.memory_used, info.mark)

def async_function_decorator(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

def judgement(problem : Problem, code : str, lang : ProgrammingLanguage, slot_function = _slot):
    @async_function_decorator
    def slot(*args, **kwargs):
        slot_function(*args, **kwargs)
    @async_function_decorator
    def clean(need_remove):
        for i in need_remove:
            try:
                os.remove(i)
            except:
                pass
    subtasks = problem.subtasks()
    if not os.path.isdir(os.path.abspath(CORE.run_sandbox)):
        os.mkdir(CORE.run_sandbox)
    uuid = str(uuid4())
    need_remove = []
    source = os.path.abspath("{}/{}.cpp".format(CORE.run_sandbox, uuid))
    need_remove.append(source)
    with open(source, "w", encoding="utf-8") as f:
        f.write(code)
    executable = os.path.abspath("{}/{}.exe".format(CORE.run_sandbox, uuid))
    need_remove.append(executable)
    source = "\"{}\"".format(source)
    executable = "\"{}\"".format(executable)
    if problem.type() == "interactive_noi":
        library_ = "{}/libraries/{}".format(problem.path, problem.data["interactive_library"])
        library = os.path.abspath("{}/{}.noiintlib.cpp".format(CORE.run_sandbox, uuid))
        need_remove.append(library)
        shutil.copyfile(library_, library)
        source += " \"{}\"".format(library)
    sig = lang.run_compile(source, executable)
    if sig != CompilationFinished():
        clean(need_remove)
        return [COMPILE_ERROR, sig, 0]
    if problem.judger().id == "testlib":
        testlib_source = os.path.abspath("{}/{}.checker.cpp".format(CORE.run_sandbox, uuid))
        shutil.copyfile(problem.judger().kwargs["path"], testlib_source)
        testlib_executable = os.path.abspath("{}/{}.checker.exe".format(CORE.run_sandbox, uuid))
        need_remove.append(testlib_source)
        need_remove.append(testlib_executable)
        testlib_source = "\"{}\"".format(source)
        testlib_executable = "\"{}\"".format(executable)
        sig = CPP.run_compile(testlib_source, testlib_executable)
        if sig != CompilationFinished():
            clean(need_remove)
            return [TESTLIB_COMPILE_ERROR, sig, 0]
    if problem.judger().id == "testlib":
        judger = TestlibJudger(path = testlib_executable)
    elif problem.judger().id == "real":
        judger = RealCompare(precision = problem.judger().kwargs["precision"])
    elif problem.judger().id == "strict":
        judger = StrictCompare()
    else:
        judger = RowCompare()
    accepted = []
    total = []
    slot(JudgeInfo(-1, "", "", sig, 0, 0, 0))
    for cnt, i in enumerate(subtasks):
        answer = 0
        skipped = False
        for j in i.required:
            if not accepted[j - 1]:
                skipped = True
                break
        if i.method == "min" and len(i.testcases) > 0:
            answer = pow(2, 31)
        now_ac = True
        for j in i.testcases:
            if skipped:
                slot(JudgeInfo(cnt+1, j.short_in, j.short_out, Skipped(_("core.problem.skipped")), 0, 0, 0))
                continue
            sig = lang.run_interpret(executable, Limits(j.time, j.memory), j.in_)
            if sig == NextJudge():
                out = sig.output
                with open(j.out, "r", encoding="utf-8") as f:
                    ans = f.read()
                with open(j.in_, "r", encoding="utf-8") as f:
                    in_ = f.read()
                osig = judger.judge(in_, out, ans)
                osig.time = sig.time_used
                osig.memory_used = sig.memory_used
                tmark = 0
                if osig == Accepted():
                    tmark = j.mark
                    if i.method == "max":
                        answer = max(answer, float(j.mark))
                    if i.method == "min":
                        answer = min(answer, float(j.mark))
                    if i.method == "sum":
                        answer = (answer + float(j.mark))
                elif osig == PartiallyCorrect():
                    now_ac = False
                    if osig.is_points:
                        tmark = osig.points
                    else:
                        tmark = j.mark * osig.partially
                    if i.method == "max":
                        answer = max(answer, tmark)
                    if i.method == "min":
                        answer = min(answer, tmark)
                    if i.method == "sum":
                        answer = (answer + tmark)
                else:
                    now_ac = False
                    if i.method == "min":
                        skipped = True
                        answer = 0
                slot(JudgeInfo(cnt + 1, j.short_in, j.short_out, osig, sig.time_used, sig.memory_used, tmark))
            else:
                now_ac = False
                slot(JudgeInfo(cnt + 1, j.short_in, j.short_out, sig, sig.time_used, sig.memory_used, 0))
                if i.method == "min":
                    skipped = True
                    answer = 0
        accepted.append(now_ac)
        total.append(answer)
    result = 0
    if problem.data["all"]["method"] == "sum":
        result = sum(total)
    elif problem.data["all"]["method"] == "min":
        result = min(total)
    elif problem.data["all"]["method"] == "max":
        result = max(total)
    clean(need_remove)
    return [COMPILE_FINISHED, total, result]
