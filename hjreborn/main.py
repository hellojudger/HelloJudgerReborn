from hjreborn.frontend.judge import main as judge_main, langs
from hjreborn.frontend.problen_maker import main as problem_maker_main
from hjreborn.frontend.utils import con
import click
import os
import shutil
from hjreborn.core.config import CORE
from urllib.request import urlretrieve
import sys


def exception_hook(etype, value, tb):
    con.log_err("发生异常：" + repr(value))
    exit(-1)


if __name__ == "__main__":
    sys.excepthook = exception_hook


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
@click.option("--tmpfilestestlib/--no-tmpfilestestlib", default=True, is_flag=True)
@click.option("--tmpfilesrun/--no-tmpfilesrun", default=True, is_flag=True)
@click.option("--submission/--no-submission", default=True, is_flag=True)
def clean(tmpfilestestlib: bool, tmpfilesrun: bool, submission: bool):
    with con.status("清理中..."):
        if tmpfilestestlib:
            for i in os.listdir(CORE.testlib_sandbox):
                if i != "testlib.h":
                    os.remove(CORE.testlib_sandbox + "/" + i)
        if tmpfilesrun:
            shutil.rmtree(CORE.run_sandbox)
        if submission:
            for i in os.listdir("."):
                if i.startswith("hjreborn-submission-"):
                    os.remove(i)
    con.log_success("清理完成。")


@group.command()
@click.argument("name")
def download(name):
    if name == "testlib":
        con.log_attention("正在从 Github 下载 Testlib...")
        if not os.path.isdir(CORE.testlib_sandbox):
            os.mkdir(CORE.testlib_sandbox)
        urlretrieve(
            "https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h",
            CORE.testlib_sandbox + "/testlib.h",
        )
    else:
        con.log_err("未知的资源名。")


@group.command()
def listlang():
    con.log_attention("可用的评测语言列表：")
    con.print(" ".join(langs.keys()))


@group.command()
def welcome():
    con.log_success("欢迎使用 Hello Judger Reborn。")
    con.log_attention("1. 请使用 hjreborn create 创建题目。")
    con.log_attention(
        "2. 请使用 hjreborn judge {题目文件夹} {源代码} [--lang=评测语言] 评测题目。"
    )
    con.log_attention("3. 请使用 hjreborn clean 清理垃圾文件。")
    con.log_attention(
        "4. 请使用 hjreborn download testlib 下载 Testlib（需要连接到 Github）。"
    )
    con.log_attention("5. 请使用 hjreborn listlang 查看评测语言列表。")
    con.log_attention("6. 请使用 hjreborn welcome 查看帮助。")


if __name__ == "__main__":
    group()
