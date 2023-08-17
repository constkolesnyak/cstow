import subprocess
from typing import Callable

from .command import CmdAction, CmdVars
from .config import Config
from .view import View

Proc = subprocess.CompletedProcess[bytes]
Run = Callable[[str], Proc]


def _run(cmd: str) -> Proc:
    return subprocess.run(args=[cmd], shell=True, capture_output=True)


def stow(config: Config, view: View, action: CmdAction, run: Run = _run) -> None:
    view.handle_action(action)

    for target, dir_ in config.each_target_and_dir():
        view.handle_dir(dir_)

        cmd: str = CmdVars(action, dir_, target).cmd(config.cmd_template)
        proc: Proc = run(cmd)  # todo exceptions

        view.handle_proc(proc)
