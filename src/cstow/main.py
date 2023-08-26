import sys
from typing import Any, NoReturn

import fire  # type: ignore

from cstow.command import CmdAction, InvalidCmdActionError
from cstow.config import Config, ConfigError
from cstow.stow import stow
from cstow.view import PlainView, RichView, View

_ACTION_DEFAULT = CmdAction.NO


def _help() -> str:
    '''Construct the help page. Let Fire generate boilerplate.'''
    actions = ', '.join(CmdAction).replace(_ACTION_DEFAULT, _ACTION_DEFAULT + ' (default)')

    return f'''
    https://github.com/constkolesnyak/cstow/blob/main/README.md

    Args:
        action: Actions: {actions}. 
        plain: Print plain text only. 
    '''


def _error(*args: Any, **kwargs: Any) -> NoReturn:
    '''Print the error(s) and exit with 1.'''
    print('ERROR:\n', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def _cli(action: str = _ACTION_DEFAULT, /, *, plain: bool = False) -> None:
    '''Use with Fire.'''
    view: View = PlainView() if plain else RichView()

    try:
        config: Config = Config.from_env_var()
        stow(CmdAction(action), config, view)
    except (ConfigError, InvalidCmdActionError) as e:
        _error(e)


def main() -> None:
    '''The entry point.'''
    _cli.__doc__ = _help()
    fire.Fire(_cli)  # type: ignore


if __name__ == '__main__':
    _cli()
