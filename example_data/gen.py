import random

for i in range(1, 11):
    for j in range(1, 11):
        a = random.randint(1, 10 ** i)
        b = random.randint(1, 10 ** i)
        with open(f"{i}-{j}.in", "w") as f:
            f.write(f"{a} {b}\n")
        with open(f"{i}-{j}.out", "w") as f:
            f.write(f"{a + b}\n")
