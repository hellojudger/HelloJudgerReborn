# pylint:disable = all
from hjreborn.i18n import _

class CoreSignal:
    signame : str = ""
    message : str = ""

    def __init__(self, message : str = ""):
        self.message = message
    
    def __str__(self):
        return self.name() + " : " + self.message

    def type(self):
        return self.signame
    
    def __eq__(self, x):
        return x.signame == self.signame

    def name(self):
        return _("core.signals." + self.signame)


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

class TimeLimitExceeded(InterpretionSignal):
    signame = "tle"

class MemoryLimitExceeded(InterpretionSignal):
    signame = "mle"

class ProgramRuntimeError(InterpretionSignal):
    signame = "re"
    code = 0

class NextJudge(InterpretionSignal):
    signame = "nj"
    output = ""

class JudgeSignal(CoreSignal):
    pass

class TestlibSignal(JudgeSignal):
    pass

class Accepted(TestlibSignal):
    signame = "ac"

class WrongAnswer(JudgeSignal):
    signame = "wa"

class JudgeFailed(JudgeSignal):
    signame = "jf"

class PartiallyCorrect(TestlibSignal):
    signame = "pc"
    is_points = False
    points = 0
    partially = 0.0

class ProblemSignal(CoreSignal):
    pass

class ProblemFileInvalid(ProblemSignal):
    signame = "pfi"

class ProblemFileValid(ProblemSignal):
    signame = "pfv"

class Skipped(CoreSignal):
    signame = "sk"

class Unaccepted(CoreSignal):
    signame = "unac"
