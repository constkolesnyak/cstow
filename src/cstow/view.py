import sys
from abc import ABC, abstractmethod
from subprocess import CompletedProcess

from path import Path

from cstow.stower import CmdAction


class View(ABC):
    @abstractmethod
    def handle_action(self, action: CmdAction) -> None:
        pass

    @abstractmethod
    def handle_dir(self, dir_: Path) -> None:
        pass

    @abstractmethod
    def handle_proc(self, proc: CompletedProcess[bytes]) -> None:
        pass


class PlainView(View):
    def handle_action(self, action: CmdAction) -> None:
        if action == CmdAction.NO:
            print(f'@@@@@ NO ACTION @@@@@\n')

    def handle_dir(self, dir_: Path) -> None:
        print(f'### {dir_} ###\n')

    def handle_proc(self, proc: CompletedProcess[bytes]) -> None:
        if stdout := proc.stdout.decode():
            print(stdout)
        if stderr := proc.stderr.decode():
            print(stderr, file=sys.stderr)


class RichView(View):
    ...
