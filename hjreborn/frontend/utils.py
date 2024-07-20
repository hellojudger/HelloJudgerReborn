import rich.console
import simplejson
import rich.prompt
import rich.markdown
from typing import Union, Optional, List

__all__ = ["con"]


class TextMarkup:
    text: str = None

    def __init__(self, text: str):
        self.text = text

    def bold(self):
        return TextMarkup(f"[bold]{self.text}[/bold]")

    def italic(self):
        return TextMarkup(f"[italic]{self.text}[/italic]")

    def underline(self):
        return TextMarkup(f"[underline]{self.text}[/underline]")

    def link(self, url: str):
        return TextMarkup(f"[link={url}]{self.text}[/link]")

    def blink(self):
        return TextMarkup(f"[blink]{self.text}[/blink]")

    def strike(self):
        return TextMarkup(f"[strike]{self.text}[/strike]")

    def color(self, color: str):
        return TextMarkup(f"[{color}]{self.text}[/{color}]")

    def done(self) -> str:
        return self.text

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"TextMarkup({self.text})"

    def __add__(self, other):
        return TextMarkup(f"{self.text}{other.text}")

    def __radd__(self, other):
        return TextMarkup(f"{other.text}{self.text}")

    def __mul__(self, other):
        return TextMarkup(self.text * other)


class Console:
    console: rich.console.Console = None

    def __init__(self):
        self.console = rich.console.Console(record = True)

    @staticmethod
    def mark(text: str) -> TextMarkup:
        return TextMarkup(text)

    def print(self, *args, sep=" ", end="\n", justify : Optional[str] = None):
        args = list(args)
        for i in range(len(args)):
            if isinstance(args[i], TextMarkup):
                args[i] = args[i].done()
        self.console.print(*args, sep=sep, end=end, justify=justify)

    def input(self, prompt: str, default: str = None, password: bool = False, choice :Optional[List[str]] = None) -> str:
        text = rich.prompt.Prompt.ask(prompt = prompt, console = self.console, password = password, choices = choice, default = default)
        if text is None:
            text = ""
        return text
    
    def confirm(self, prompt: str, default: bool = True) -> bool:
        return rich.prompt.Confirm.ask(prompt = prompt, console = self.console, default = default)

    def json(self, data : Union[str, list, dict]):
        if not isinstance(data, str):
            data_ = simplejson.dumps(data, indent=4)
        self.console.print_json(data_)

    def error(self):
        self.console.print_exception()

    def chapter(self, text : str):
        self.console.rule(text)

    def status(self, text : str, spinner : str = "dots"):
        return self.console.status(text, spinner = spinner)
    
    def export_html(self):
        return self.console.export_html()

    def markdown(self, text : str):
        obj = rich.markdown.Markdown(text)
        self.console.print(obj)

    def log_err(self, text : str):
        self.print(self.mark(text).bold().color("red"))

    def log_success(self, text : str):
        self.print(self.mark(text).bold().color("green"))

    def log_attention(self, text : str):
        self.print(self.mark(text).bold().color("yellow"))
    
con = Console()
