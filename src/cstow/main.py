import sys
from typing import Any, NoReturn

import fire  # type: ignore

from cstow.config import (
    CmdAction,
    Config,
    ConfigEnvVarUnsetError,
    InvalidActionError,
    InvalidConfigError,
)
from cstow.stow import stow
from cstow.view import PlainView


def _error(*args: Any, **kwargs: Any) -> NoReturn:
    print('ERROR:\n', file=sys.stderr)
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def _cli(action: CmdAction = CmdAction.NO) -> None:
    try:
        config: Config = Config.from_env_var()
        stow(config, PlainView(), action)
    except (
        InvalidConfigError,
        ConfigEnvVarUnsetError,
        FileNotFoundError,
        InvalidActionError,
    ) as e:
        _error(e)


def main() -> None:
    fire.Fire(_cli)  # type: ignore
