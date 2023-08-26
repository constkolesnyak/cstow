import sys
from abc import ABC, abstractmethod
from subprocess import CompletedProcess

from path import Path

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


class RichView(View):
    '''The view for printing rich text.'''

    def show_action(self, action: CmdAction) -> None:
        ...

    def show_dir(self, dir_: Path) -> None:
        ...

    def show_proc(self, proc: CompletedProcess[bytes]) -> None:
        ...


def _action_to_title(action: CmdAction) -> str:
    return action.replace(CmdAction.NO, 'dry run').upper()
