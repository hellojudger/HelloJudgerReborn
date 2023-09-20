# pylint:disable = all
from core.run import CPP_14, Limits


print(CPP_14.run_compile("1.cpp", "1.exe"))
print(CPP_14.run_interpret("1.exe", Limits(1000, 1024 * 1024)))
