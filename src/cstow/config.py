import copy
import itertools
import os
import tomllib
from functools import partial
from string import Template
from typing import Annotated, Iterator, Optional, Self

import attrs
import pydantic as pd
from path import Path

from cstow.command import COMMAND_TEMPLATE_DEFAULT, CmdVars

TarsDirsStr = dict[str, list[str]]
TarsDirsPath = dict[Path, list[Path]]


_CONFIG_PATH_ENV_VAR = 'CSTOW_CONFIG_PATH'


class ConfigError(Exception):
    ''''''


class ConfigEnvVarUnsetError(ConfigError):
    def __init__(self, env_var: str) -> None:
        super().__init__(
            f'Environment variable {env_var} is unset. Expected path to cstow_config.toml'
        )


class ConfigNotFoundError(ConfigError):
    def __init__(self, path: str) -> None:
        super().__init__(f'No such file: {path}')


class InvalidConfigError(ConfigError):
    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"Config is invalid: '{path}'\n\n{message}")

    @classmethod
    def from_pydantic(cls, path: str, exception: pd.ValidationError) -> Self:
        messages: list[str] = []

        for err in exception.errors():
            loc = err['loc'][0]
            inp = err['input']
            msg = err['msg'].lstrip('Assertion failed, ')
            messages.append(f"{loc}\n    input: '{inp}'\n    error: {msg}")

        return cls(path, '\n\n'.join(messages))


def _validate_cmd_template(template_str: str) -> Template:
    template = Template(template_str)

    assert template.is_valid(), "Invalid syntax in 'cmd_template'"
    assert set(template.get_identifiers()) == set(
        CmdVars.fields()
    ), f"'cmd_template' must contain all of these vars and no others: " + ", ".join(
        CmdVars.fields()
    )

    return template


CmdTemplate = Annotated[str, pd.AfterValidator(_validate_cmd_template)]


class Config(pd.BaseModel, extra='forbid'):
    cmd_template: CmdTemplate


class _OldRawConfig(pd.BaseModel, extra='forbid'):
    cmd_template: str = COMMAND_TEMPLATE_DEFAULT
    root_dir: str = Path('/')
    targets_dirs: TarsDirsStr

    config_path: str

    @classmethod
    def from_env_var(cls, env_var: str) -> "_OldRawConfig":
        return cls.from_path(_env_var_to_path(env_var))

    @classmethod
    def from_path(cls, path: Path) -> "_OldRawConfig":
        try:
            return cls(**tomllib.loads(path.read_text()), config_path=path)
        except FileNotFoundError:
            raise ConfigNotFoundError(path)
        except (tomllib.TOMLDecodeError, pd.ValidationError) as e:
            raise InvalidConfigError(path, str(e))
        except TypeError:
            raise InvalidConfigError(path, 'config_path\n  Extra keys are not permitted')


def _env_var_to_path(env_var: str) -> Path:
    try:
        return Path(os.environ[env_var])
    except KeyError:
        raise ConfigEnvVarUnsetError(env_var)


@attrs.define
class OldConfig:
    cmd_template: Template
    targets_dirs: TarsDirsPath = attrs.field(converter=copy.deepcopy)  # type: ignore
    _root_dir: Path

    @classmethod
    def _from_raw_config(cls, raw_cfg: _OldRawConfig) -> "OldConfig":
        cmd_template: Optional[Template] = _validate_cmd_template(raw_cfg.cmd_template)
        if cmd_template is None:
            raise InvalidConfigError(
                raw_cfg.config_path,
                f"'cmd_template' is invalid:\n{raw_cfg.cmd_template}",
            )

        # todo FileNotFound -> InvalidConfig exceptions
        root_dir: Path = _str_to_dir(raw_cfg.root_dir)
        targets_dirs: TarsDirsPath = _tds_to_tdp(raw_cfg.targets_dirs, root_dir)

        return cls(cmd_template, targets_dirs, root_dir)

    @classmethod
    def from_env_var(cls, env_var: str = _CONFIG_PATH_ENV_VAR) -> "OldConfig":
        return OldConfig._from_raw_config(_OldRawConfig.from_env_var(env_var))

    def each_target_and_dir(self) -> Iterator[tuple[Path, Path]]:
        for target, dirs in self.targets_dirs.items():
            yield from itertools.product((target,), dirs)


def _tds_to_tdp(targets_dirs: TarsDirsStr, root_dir: Path) -> TarsDirsPath:
    return {
        _str_to_dir(target): list(map(partial(_str_to_dir, root_dir=root_dir), dirs))
        for target, dirs in targets_dirs.items()
    }


def _str_to_dir(path_str: str, root_dir: Path = Path('/')) -> Path:
    path: Path = root_dir / Path(path_str).expand()
    if path.isdir():
        return path
    raise FileNotFoundError(f"Directory '{path}' is not found")
