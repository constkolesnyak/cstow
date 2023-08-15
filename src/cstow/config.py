import copy
import os
import tomllib
from enum import StrEnum, auto
from functools import partial
from string import Template
from typing import Optional

import attrs
import pydantic
from path import Path

TarsDirsStr = dict[str, list[str]]
TarsDirsPath = dict[Path, list[Path]]


class CmdVars(StrEnum):
    ACTION = auto()
    DIRECTORY = auto()
    TARGET = auto()


_CONFIG_PATH_ENV_VAR = 'CSTOW_CONFIG_PATH'
_COMMAND_TEMPLATE_DEFAULT: str = (
    "stow --'${}' --no-folding --verbose -d '${}' -t '${}' . 2>&1 | grep -v -e '^BUG' -e '^WARN'"
).format(*CmdVars)


class ConfigEnvVarUnsetError(Exception):
    def __init__(self, env_var: str) -> None:
        super().__init__(
            f'Environment variable {env_var} is unset. Expected path to cstow_config.toml'
        )


class InvalidConfigError(Exception):
    def __init__(self, path: str, message: Exception | str) -> None:
        super().__init__(f"Config '{path}' is invalid:\n{message}")


class _RawConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='forbid')

    cmd_template: str = _COMMAND_TEMPLATE_DEFAULT
    root_dir: str = Path('/')
    targets_dirs: TarsDirsStr

    config_path: str

    @classmethod
    def from_env_var(cls, env_var: str) -> "_RawConfig":
        return cls.from_path(_env_var_to_path(env_var))

    @classmethod
    def from_path(cls, path: Path) -> "_RawConfig":
        try:
            return cls(**tomllib.loads(path.read_text()), config_path=path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config '{path}' is not found")
        except (tomllib.TOMLDecodeError, pydantic.ValidationError) as e:
            raise InvalidConfigError(path, e)
        except TypeError:
            raise InvalidConfigError(path, 'config_path\n  Extra keys are not permitted')


def _env_var_to_path(env_var: str) -> Path:
    try:
        return Path(os.environ[env_var])
    except KeyError:
        raise ConfigEnvVarUnsetError(env_var)


@attrs.define
class Config:
    cmd_template: Template
    targets_dirs: TarsDirsPath = attrs.field(converter=copy.deepcopy)  # type: ignore
    _root_dir: Path

    @classmethod
    def _from_raw_config(cls, raw_cfg: _RawConfig) -> "Config":
        cmd_template: Optional[Template] = _str_to_cmd_template(raw_cfg.cmd_template)
        if cmd_template is None:
            raise InvalidConfigError(
                raw_cfg.config_path,
                f"'cmd_template' is invalid:\n{raw_cfg.cmd_template}",
            )

        root_dir: Path = _str_to_dir(raw_cfg.root_dir)
        targets_dirs: TarsDirsPath = _tds_to_tdp(raw_cfg.targets_dirs, root_dir)

        return cls(cmd_template, targets_dirs, root_dir)

    @classmethod
    def from_env_var(cls, env_var: str = _CONFIG_PATH_ENV_VAR) -> "Config":
        return Config._from_raw_config(_RawConfig.from_env_var(env_var))


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


def _str_to_cmd_template(template_str: str) -> Optional[Template]:
    template = Template(template_str)
    if template.is_valid() and set(template.get_identifiers()) == set(CmdVars):
        return template
    return None
