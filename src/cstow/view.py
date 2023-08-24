import sys
from abc import ABC, abstractmethod
from subprocess import CompletedProcess

from path import Path

from cstow.command import CmdAction


class View(ABC):
    '''The view for showing information to the user.'''

    @abstractmethod
    def show_action(self, action: CmdAction) -> None:
        ''''''

    @abstractmethod
    def show_dir(self, dir_: Path) -> None:
        ''''''

    @abstractmethod
    def show_proc(self, proc: CompletedProcess[bytes]) -> None:
        ''''''


class PlainView(View):
    '''The view for printing plain text only.'''

    def show_action(self, action: CmdAction) -> None:
        if action == CmdAction.NO:
            print(f'@@@@@ NO ACTION @@@@@\n')

    def show_dir(self, dir_: Path) -> None:
        print(f'### {dir_} ###\n')

    def show_proc(self, proc: CompletedProcess[bytes]) -> None:
        if stdout := proc.stdout.decode():
            print(stdout)
        if stderr := proc.stderr.decode():
            print(stderr, file=sys.stderr)


class RichView(View):
    '''The view for printing rich text.'''

    ...
