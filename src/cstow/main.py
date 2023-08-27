import sys
from typing import Any, NoReturn

import fire  # type: ignore

from cstow.command import CmdAction, InvalidCmdActionError, str_to_action
from cstow.config import Config, ConfigError
from cstow.stow import stow
from cstow.view import PlainView, RichView, View


def _error(*args: Any, **kwargs: Any) -> NoReturn:
    '''Print the error(s) and exit with 1.'''
    print('ERROR:\n', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def _cli(action: str = 'no', *, plain: bool = False) -> None:
    '''Use with Fire.'''
    view: View = PlainView() if plain else RichView()

    try:
        config: Config = Config.from_env_var()
        stow(str_to_action(action), config, view)
    except (ConfigError, InvalidCmdActionError) as e:
        _error(e)


def main() -> None:
    '''
    The entry point.

    Customize the help page, fire up the fire.Fire.
    '''

    _cli.__doc__ = f'''
    https://github.com/constkolesnyak/cstow/blob/main/README.md

    Args:
        action: Actions: {', '.join(CmdAction)}. 
        plain: Print plain text only. 
    '''

    fire.Fire(_cli)  # type: ignore


if __name__ == '__main__':
    _cli()
