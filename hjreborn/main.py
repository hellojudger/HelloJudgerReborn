from hjreborn.frontend.judge import main as judge_main
from hjreborn.frontend.problen_maker import main as problem_maker_main
from hjreborn.frontend.utils import con
import click
import os
import shutil
from hjreborn.core.config import CORE

@click.group(cls=click.Group)
def group():
    pass

@group.command()
@click.argument("path")
@click.argument("file")
@click.option("--lang", default="ccf")
def judge(*args, **kwargs):
    judge_main(*args, **kwargs)

@group.command()
def create():
    problem_maker_main()

@group.command()
def clean():
    if os.path.isdir(CORE.testlib_sandbox):
        shutil.rmtree(CORE.testlib_sandbox)
        con.log_success("已清理 Testlib 垃圾文件。")
    if os.path.isdir(CORE.run_sandbox):
        shutil.rmtree(CORE.run_sandbox)
        con.log_success("已清理测试文件。")
    for i in os.listdir("."):
        j = str(i)
        if j.startswith("hjreborn-submission-"):
            os.remove(j)
    con.log_success("已清理提交记录文件。")

if __name__ == "__main__":
    group()
