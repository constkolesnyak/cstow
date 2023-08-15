import itertools
from enum import StrEnum, auto
from subprocess import CompletedProcess, run
from typing import Iterator

from path import Path

from cstow.config import CmdVars, Config


class CmdAction(StrEnum):
    NO = auto()
    RESTOW = auto()
    DELETE = auto()


# Put it here to resolve circular import
from cstow.view import View


class InvalidActionError(Exception):
    def __init__(self, action: str) -> None:
        super().__init__(
            f"Action '{action}' is invalid\nUse one of these: " + ', '.join(CmdAction)
        )


class Stower:
    def __init__(self, config: Config, view: View, action: CmdAction) -> None:
        self.config: Config = config
        self.view: View = view

        if action not in list(CmdAction):
            raise InvalidActionError(action)
        self.action: CmdAction = action

    def stow(self) -> None:
        self.view.handle_action(self.action)

        for target, dir_ in self._each_target_and_dir():
            self.view.handle_dir(dir_)

            cmd: str = self._create_cmd(target, dir_)
            proc: CompletedProcess[bytes] = run(args=[cmd], shell=True, capture_output=True)
            # todo exceptions

            self.view.handle_proc(proc)

    def _each_target_and_dir(self) -> Iterator[tuple[Path, Path]]:
        for target, dirs in self.config.targets_dirs.items():
            yield from itertools.product((target,), dirs)

    def _create_cmd(self, target: Path, dir_: Path) -> str:
        return self.config.cmd_template.substitute(
            **{
                CmdVars.ACTION: self.action,
                CmdVars.DIRECTORY: dir_,
                CmdVars.TARGET: target,
            }
        )
