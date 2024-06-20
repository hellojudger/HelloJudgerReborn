from rich.console import Console
from rich.prompt import Prompt, Confirm
import click

console = Console()

@click.group(cls=click.Group)
def welcome():
    console.print("Welcome to Hello Judger Reborn.", style="green bold")

@welcome.command()
@click.argument("path")
def test(path):
    """评测一个题目"""
    pass


def get_time(prompt: str):
    while True:
        ret = Prompt.ask(f"[bold]{prompt}[/bold]", default="1s")
        units = {"ms" : 1, "s" : 1000, "min" : 60000, "h" : 3600000, "d" : 24 * 3600000, "us" : 1 / 1000, "ns" : 1 / 1000 / 1000}
        checked = False
        zero = False
        negative = False
        too_big = False
        int_part = ""
        for i in units.keys():
            if ret.endswith(i):
                int_part = ret[:-len(i)]
                try:
                    int_part = float(int_part)
                    int_part = round(int_part * units[i])
                except ValueError:
                    checked = True
                else:
                    if int_part == 0:
                        checked = True
                        zero = True
                        break
                    if int_part < 0:
                        checked = True
                        negative = True
                        break
                    if int_part > 31536000000:
                        too_big = True
                        checked = True
                        break
                    return int_part
        if not checked:
            console.print(f"[red bold]单位不支持或未输入单位。支持的单位：{','.join(list(units.keys()))}（区分大小写）。[/ red bold]")
        elif zero:
            console.print("[red bold]您输入的数值转换为毫秒后四舍五入为 0ms，请尝试更大的合法数值。[/ red bold]")
        elif negative:
            console.print(f"[red bold]您输入的数值转换后为 {int_part}ms，尚不支持负数。[/ red bold]")
        elif too_big:
            console.print("[red bold]您输入的值超过了 365d，请尝试输入一个更小的合法数值。[/ red bold]")
        else:
            console.print(f"[red bold]{repr(int_part)} 无法识别为实数。[/ red bold]")


@welcome.command()
@click.argument("path")
def create(path):
    """创建一个题目"""
    name = Prompt.ask("[bold]题目名[/ bold]", default="unnamed")
    type_ = Prompt.ask("[bold]题目类型[/bold]", choices=["traditional", "interactive_noip"], default="traditional")
    p_count = 0
    while True:
        p_count += 1
        have_statement = Confirm.ask(f"[bold]您是否有第 {p_count} 个题面？[/ bold]", default=False)
        if have_statement:
            p_type = Prompt.ask(f"[bold]#{p_count} 类型[/ bold]", choices=["md", "html", "pdf"], default="md")
            p_path = Prompt.ask(f"[bold]#{p_count} 位置[/ bold]")
            p_name = Prompt.ask(f"[bold]#{p_count} 名称[/ bold]", default=f"题面 #{p_count}")
        else:
            console.print("[bold green]题面录入完成。[/bold green]")
            break
    while True:
        print(get_time("时间限制"))


if __name__ == "__main__":
    welcome()
