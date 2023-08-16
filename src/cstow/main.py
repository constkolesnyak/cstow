import sys
from typing import Any, NoReturn

import fire  # type: ignore

from cstow.config import Config, ConfigEnvVarUnsetError, InvalidConfigError
from cstow.stower import CmdAction, InvalidActionError, Stower
from cstow.view import PlainView


def _error(*args: Any, **kwargs: Any) -> NoReturn:
    print('ERROR:\n', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def _cli(action: CmdAction = CmdAction.NO) -> None:
    try:
        config: Config = Config.from_env_var()
        stower = Stower(config, PlainView(), action)
        stower.stow()
    except (
        InvalidConfigError,
        ConfigEnvVarUnsetError,
        FileNotFoundError,
        InvalidActionError,
    ) as e:
        _error(e)


def main() -> None:
    fire.Fire(_cli)  # type: ignore
