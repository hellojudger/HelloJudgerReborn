# pylint:disable = all
from core.judger import TestlibJudger

j = TestlibJudger(path="spj")
j.judge("", "1 2 3", "1 2 3")
