# pylint: disable=all
import subprocess
import psutil
from os import PathLike, system as run_shell
from hjreborn.core.signals import *
from hjreborn.core.config import CORE
from os.path import abspath
from platform import system
from hjreborn.i18n import _
import time


class Limits:
    memory_limit : int = 0
    time_limit : int = 0

    def __init__(self, time_limit : int, memory_limit : int):
        self.memory_limit = memory_limit
        self.time_limit = time_limit


class ProgrammingLanguage:
    compile_format : str = ""
    interpret_format : str = ""

    def __init__(self, compile_format : str, interpret_format : str):
        self.compile_format = compile_format
        self.interpret_format = interpret_format

    def run_compile(self, source : PathLike, executable : PathLike):
        if self.compile_format == "":
            return CompilationFinished(_("core.run.compilationFinished"))
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
        if killed:
            return CompilationTimeout(_("core.run.compilationTimeout"))
        if process.returncode != 0:
            stderr = process.communicate()[1]
            err = stderr.decode("utf-8")
            return CompilationError(_("core.run.compilationError").format(err=err, code=process.returncode))
        return CompilationFinished(_("core.run.compilationFinished"))

    def run_interpret(self, executable : PathLike, limits : Limits, stdin : PathLike = None):
        if system() == "Linux":
            run_shell("chmod +x {}".format(executable.split(' ')[0]))
        if stdin is not None:
            stdin = open(stdin)
        else:
            stdin = subprocess.PIPE
        proc = subprocess.Popen(executable, stdin=stdin, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
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
        if tle:
            obj = TimeLimitExceeded(_("core.run.timeLimitExceeded"))
        elif mle:
            obj = MemoryLimitExceeded(_("core.run.memoryLimitExceeded"))
        elif proc.returncode != 0:
            obj = ProgramRuntimeError(_("core.run.programRuntimeError").format(code=proc.returncode))
            obj.code = proc.returncode
        else:
            stdout = proc.communicate()[0]
            obj = NextJudge(_("core.run.nextJudge"))
            obj.output = stdout.decode("utf-8")
        obj.memory_used = memory
        obj.time_used = (end - start) * 1000
        return obj

CPP = ProgrammingLanguage("g++ -o {executable} {source} -O2", "{executable}")