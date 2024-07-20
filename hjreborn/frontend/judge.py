from hjreborn.frontend.utils import con, TextMarkup
from hjreborn.core.problem import judgement, validate, JudgeInfo, SubtaskInfo, Problem
from hjreborn.core.problem import TESTLIB_COMPILE_ERROR, COMPILE_ERROR, COMPILE_FINISHED
from hjreborn.core.run import ProgrammingLanguage
from hjreborn.core.signals import *
import os
import simplejson
import uuid
import subprocess
import platform
from typing import Union

def gen_uuid() -> str:
    return str(uuid.uuid4())

def gcc_like(*args) -> ProgrammingLanguage:
    return ProgrammingLanguage("g++ -o {executable} {source} " + ' '.join(args), "{executable}")
      
langs = {
    "cpp98" : gcc_like("-std=c++98"),
    "cpp98o2" : gcc_like("-std=c++98", "-O2"),
    "cpp98o3" : gcc_like("-std=c++98", "-O3"),
    "cpp98ofast" : gcc_like("-std=c++98", "-Ofast"),
    "cpp11" : gcc_like("-std=c++11"),
    "cpp11o2" : gcc_like("-std=c++11", "-O2"),
    "cpp11o3" : gcc_like("-std=c++11", "-O3"),
    "cpp11ofast" : gcc_like("-std=c++11", "-Ofast"),
    "cpp14" : gcc_like("-std=c++14"),
    "cpp14o2" : gcc_like("-std=c++14", "-O2"),
    "cpp14o3" : gcc_like("-std=c++14", "-O3"),
    "cpp14ofast" : gcc_like("-std=c++14", "-Ofast"),
    "cpp17" : gcc_like("-std=c++17"),
    "cpp17o2" : gcc_like("-std=c++17", "-O2"),
    "cpp17o3" : gcc_like("-std=c++17", "-O3"),
    "cpp17ofast" : gcc_like("-std=c++17", "-Ofast"),
    "cpp20" : gcc_like("-std=c++20"),
    "cpp20o2" : gcc_like("-std=c++20", "-O2"),
    "cpp20o3" : gcc_like("-std=c++20", "-O3"),
    "cpp20ofast" : gcc_like("-std=c++20", "-Ofast"),

    "ccf" : gcc_like("-std=c++14", "-O2"),
    "ccf_oj" : gcc_like("-std=c++14", "-O2", "-DONLINE_JUDGE")
}

ac_emoji = ":heavy_check_mark:"
wrong_emoji = ":x:"

def score_markup(score : int, total : int) -> TextMarkup:
    markup = None
    if score <= total / 3:
        markup = con.mark(str(score)).color("red")
    elif score <= total * 2 / 3:
        markup = con.mark(str(score)).color("yellow")
    elif score != total:
        markup = con.mark(str(score)).color("spring_green1")
    else:
        markup = con.mark(str(score)).color("green")
    markup += con.mark(" / ")
    markup += con.mark(str(total)).color("green")
    markup = markup.bold()
    return markup

def signal_markup(signal : Union[JudgeSignal,InterpretionSignal]) -> TextMarkup:
    markup = con.mark(signal.name())
    if signal.signame == "ac":
        markup = markup.color("green")
    elif signal.signame == "wa":
        markup = markup.color("red")
    elif signal.signame == "tle":
        markup = markup.color("purple4")
    elif signal.signame == "mle":
        markup = markup.color("purple3")
    elif signal.signame == "re":
        markup = markup.color("magenta")
    elif signal.signame == "pc":
        markup = markup.color("bright_cyan")
    elif signal.signame == "jf":
        markup = markup.color("turquoise4")
    else:
        markup = markup.color("grey37")
    return markup

def main(path, file, lang):
    if lang not in langs:
        con.log_err(f"未找到编译器 {lang}")
        return
    if not os.path.isdir(path):
        con.log_err(f"未找到题目路径 {path}")
        return
    if not os.path.isfile(file):
        con.log_err(f"未找到源文件 {file}")
        return
    con.log_attention("准备检查题目完整性。")
    validated = validate(path)
    if isinstance(validated, ProblemFileInvalid):
        con.log_err("检测到题目不完整，请检查后重试。")
        fn = f"{gen_uuid()}.log"
        with open(fn, "w", encoding="utf-8") as f:
            f.write(validated.message)
        con.log_err(f"错误信息已保存至 {fn}。请查看。")
        return
    con.log_success("检查完毕，题目完整。")

    with open(os.path.join(path, "problem.json"), "r", encoding="utf-8") as f:
        problem = simplejson.load(f)
        con.log_success(f"准备开始评测题目 ： {problem['name']}")
        # task_id_habit = problem["task_id_habit"]
        # subtask_count = len(problem["subtasks"])

    def tc_text(subtask : int, testcase : int) -> TextMarkup:
        return con.mark(f"TC {subtask} - {testcase}").color("blue").bold()
    
    def report_task(info : JudgeInfo):
        markup = con.mark("")
        emoji = wrong_emoji
        message = info.signal.message
        time_ = f"{info.time_used:.1f}ms"
        memory = f"{info.memory_used / 1024 / 1024 :.2}MB"
        if info.signal.type() == "ac":
            emoji = ac_emoji
        score = score_markup(info.mark, info.total)
        tc = tc_text(info.subtask, info.in_)
        markup += tc + con.mark(" ")
        markup += con.mark(emoji) + con.mark(" ")
        markup += signal_markup(info.signal).bold() + con.mark(" ")
        markup += con.mark(message) + con.mark(" ")
        markup += con.mark(time_).color("purple4") + con.mark(" ")
        markup += con.mark(memory).color("purple3") + con.mark(" ")
        markup += score
        con.print(markup)

    def report_subtask(info : SubtaskInfo):
        markup = con.mark(f"ST {info.subtask} ")
        if info.status.type() == "ac":
            markup += con.mark(ac_emoji)
        else:
            markup += con.mark(wrong_emoji)
        markup += con.mark(" ")
        markup += score_markup(info.mark, info.total)
        markup = markup.bold()
        con.print(markup)
    
    with open(file, "r", encoding="utf-8") as f:
        code = f.read()
    
    ans = judgement(Problem(path), code, langs[lang], report_task, report_subtask)
    if ans[0] == COMPILE_ERROR:
        con.log_err(ans[1])
        return
    elif ans[0] == TESTLIB_COMPILE_ERROR:
        con.log_err("Testlib 比较器编译错误。")
        return
    con.log_success("测试完成！")
    con.print(con.mark("得分：") + score_markup(ans[2], ans[3]))
    if ans[2] == ans[3]:
        con.log_success("恭喜你通过了本题！快去试试下一题吧！")
    elif ans[2] != 0:
        con.log_attention("很遗憾，你并没有通过本题，请尝试修改代码，然后再测试一次。")
    else:
        con.log_err("很遗憾，你爆零了，不要灰心，继续加油！")
    record = con.export_html()
    if con.confirm("是否将测试结果导出为 HTML？", default=True):
        fn = "hjreborn-submission-" + gen_uuid() + ".html"
        with open(fn, "w", encoding="utf-8") as f:
            f.write(record)
        con.log_success(f"HTML 已保存至 {fn}。")
        if con.confirm("是否立即打开导出的 HTML？", default=True):
            if platform.system() == "Windows":
                os.startfile(fn)
            else:
                subprocess.Popen(["xdg-open", fn])
