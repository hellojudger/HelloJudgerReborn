# 描述如何运行和编译一个程序的库

import subprocess
import psutil
from os import PathLike
from core.config import CORE
from i18n import _
import time


class Limits:
    memory_limit : int = 0
    time_limit : int = 0

    def __init__(self, time_limit : int, memory_limit : int):
        self.memory_limit = memory_limit
        self.time_limit = time_limit


class CoreSignal:
    signame : str = ""
    message : str = ""

    def __init__(self, message : str):
        self.message = message
    
    def __str__(self):
        return self.message

    def type(self):
        return self.signame

class CompilationSignal(CoreSignal):
    pass

class CompilationFinished(CompilationSignal):
    signame = "cf"

class CompilationError(CompilationSignal):
    signame = "ce"

class CompilationTimeout(CompilationSignal):
    signame = "ct"

class InterpretionSignal(CoreSignal):
    signame = ""
    time_used = 0
    memory_used = 0

    def __str__(self):
        return "{} Time used: {} ms Memory used: {} MB.".format(self.message, self.time_used, self.memory_used / 1024 / 1024)

class TimeLimitExceeded(InterpretionSignal):
    signame = "tle"

class MemoryLimitExceeded(InterpretionSignal):
    signame = "mle"

class ProgramRuntimeError(InterpretionSignal):
    signame = "re"

class NextJudge(InterpretionSignal):
    signame = "nj"
    output = ""


class ProgammingLanguage:
    compile_format : str = ""
    interpret_format : str = ""
    interpret_shell : bool = True

    def __init__(self, compile_format : str, interpret_format : str, interpret_shell : bool = False):
        self.compile_format = compile_format
        self.interpret_format = interpret_format
        self.interpret_shell = interpret_shell

    def run_compile(self, source : PathLike, executable : PathLike):
        compile_command = self.compile_format.format(source=source, executable=executable)
        process = subprocess.Popen(compile_command, shell=True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        start = time.perf_counter()
        end = start
        killed = False
        while process.poll() is None:
            end = time.perf_counter()
            if (end - start) * 1000 > CORE.compile_time_limit:
                killed = True
                process.kill()
                break
        process.terminate()
        stdout, stderr = process.communicate()
        if killed:
            return CompilationTimeout(_("core.run.compilationTimeout"))
        if process.returncode != 0:
            err = stderr.decode("utf-8")
            return CompilationError(_("core.run.compilationError").format(err=err, code=process.returncode))
        return CompilationFinished(_("core.run.compilationFinished"))

    def run_interpret(self, executable : PathLike, limits : Limits, stdin : PathLike = None):
        if stdin is not None:
            stdin = open(stdin)
        else:
            stdin = subprocess.PIPE
        proc = subprocess.Popen(executable, stdin=stdin, stdout=subprocess.PIPE, shell=self.interpret_shell, stderr=subprocess.PIPE)
        process = psutil.Process(proc.pid)
        start = time.perf_counter()
        end = start
        tle, mle = False, False
        memory = 0
        while proc.poll() is None:
            end = time.perf_counter()
            if (end - start) * 1000 > limits.time_limit:
                tle = True
                process.kill()
                break
            try:
                memory_info = process.memory_full_info()
            except psutil.NoSuchProcess:
                break
            memory = memory_info.uss
            if CORE.memory_type == "rss":
                memory = memory_info.rss
            if CORE.memory_type == "vms":
                memory = memory_info.vms
            if memory > limits.memory_limit:
                mle = True
                process.kill()
                break
        proc.terminate()
        stdout, stderr = proc.communicate()
        obj = None
        if tle:
            obj = TimeLimitExceeded(_("core.run.timeLimitExceeded"))
        elif mle:
            obj = MemoryLimitExceeded(_("core.run.memoryLimitExceeded"))
        elif proc.returncode != 0:
            obj = ProgramRuntimeError(_("core.run.programRuntimeError").format(code=proc.returncode))
        else:
            obj = NextJudge(_("core.run.nextJudge"))
            obj.output = stdout.decode("utf-8")
        obj.memory_used = memory
        obj.time_used = (end - start) * 1000
        return obj

CPP_14 = ProgammingLanguage("g++ -o {executable} {source} -std=c++14", "{executable}")
