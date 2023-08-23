import subprocess
from typing import Callable

from path import Path

from cstow.command import CmdAction, CmdVars
from cstow.config import Config
from cstow.view import View

Proc = subprocess.CompletedProcess[bytes]
Run = Callable[[str], Proc]


def _run(cmd: str) -> Proc:
    return subprocess.run(args=[cmd], shell=True, capture_output=True)


def stow(action: CmdAction, config: Config, view: View, run: Run = _run) -> None:
    view.handle_action(action)

    for target, dir_ in config.each_target_and_dir():
        view.handle_dir(Path(dir_))

        cmd: str = CmdVars(action, target, dir_).cmd(config.cmd_template)  # type: ignore
        proc: Proc = run(cmd)  # todo exceptions

        view.handle_proc(proc)
