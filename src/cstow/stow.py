import subprocess
from typing import Callable

from path import Path

from cstow.command import CmdAction, CmdVars
from cstow.config import Config
from cstow.view import View

Proc = subprocess.CompletedProcess[bytes]
Run = Callable[[str], Proc]


def _run(cmd: str) -> Proc:
    '''
    Run a command in the shell.

    Raises:
        OSError: If the shell is not found, which is unlikely.
    '''
    return subprocess.run(args=[cmd], shell=True, capture_output=True)


def stow(action: CmdAction, config: Config, view: View, run: Run = _run) -> None:
    '''
    Commit an action on targets and dirs from a config, show the output using a view.

    Args:
        action: A GNU Stow action.
        config: A user config.
        view: A view.
        run: A Callable to run GNU Stow commands. Defaults to _run.
    '''
    view.show_action(action)

    for target, dir_ in config.each_target_and_dir():
        view.show_dir(Path(dir_))

        cmd: str = CmdVars(action, target, dir_).cmd(config.cmd_template)  # type: ignore
        proc: Proc = run(cmd)

        view.show_proc(proc)
