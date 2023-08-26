import sys
from typing import Any, NoReturn

import fire  # type: ignore

from cstow.command import CmdAction, InvalidCmdActionError
from cstow.config import Config, ConfigError
from cstow.stow import stow
from cstow.view import PlainView


def _error(*args: Any, **kwargs: Any) -> NoReturn:
    '''Print the error(s) and exit with 1.'''
    print('ERROR:\n', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def _cli(action: CmdAction = CmdAction.NO) -> None:
    ''''''  # todo 'help' docstring
    try:
        config: Config = Config.from_env_var()
        stow(action, config, PlainView())
    except (ConfigError, InvalidCmdActionError) as e:
        _error(e)


def main() -> None:
    '''The entry point.'''
    fire.Fire(_cli)  # type: ignore


if __name__ == '__main__':
    _cli()
