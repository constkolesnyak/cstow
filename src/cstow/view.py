import os
import sys
from abc import ABC, abstractmethod
from subprocess import CompletedProcess

from path import Path
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

from cstow.command import CmdAction


class View(ABC):
    '''The view for showing information to the user.'''

    @abstractmethod
    def show_action(self, action: CmdAction) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_dir(self, dir_: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_proc(self, proc: CompletedProcess[bytes]) -> None:
        raise NotImplementedError


class PlainView(View):
    '''The view for printing plain text only.'''

    def show_action(self, action: CmdAction) -> None:
        print(f'@@@@@ {_action_to_title(action)} @@@@@\n')

    def show_dir(self, dir_: Path) -> None:
        print(f'### {dir_} ###\n')

    def show_proc(self, proc: CompletedProcess[bytes]) -> None:
        if stdout := proc.stdout.decode():
            print(stdout)
        if stderr := proc.stderr.decode():
            print(stderr, file=sys.stderr)


class _StowHighlighter(RegexHighlighter):
    """The highlighter for GNU Stow output."""

    highlights = [r'(?P<linking>(UN)?LINK)', r'(?P<linking>=>)']
    theme = Theme({"linking": "bold spring_green4"})


class RichView(View):
    '''The view for printing rich text.'''

    def __init__(self) -> None:
        self.console = Console(highlighter=_StowHighlighter(), theme=_StowHighlighter.theme)
        self.error_console = Console(stderr=True, style="red")

    def show_action(self, action: CmdAction) -> None:
        surround = '[deep_pink3]' + '@' * 15

        self.console.print(
            f'{surround}   [bold green]{_action_to_title(action)}   {surround}\n',
            justify='center',
        )

    def show_dir(self, dir_: Path) -> None:
        self.console.print(
            f"[cyan]{dir_.parent}{os.path.sep}[yellow bold]{dir_.name}\n", justify='center'
        )

    def show_proc(self, proc: CompletedProcess[bytes]) -> None:
        if stdout := proc.stdout.decode():
            self.console.print(stdout)
        if stderr := proc.stderr.decode():
            self.error_console.print('[bold]ERROR:\n')
            self.error_console.print(stderr)


def _action_to_title(action: CmdAction) -> str:
    return action.replace(CmdAction.NO, 'dry run').upper()
