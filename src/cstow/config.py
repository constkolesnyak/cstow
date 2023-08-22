import copy
import itertools
import os
import tomllib
from string import Template
from typing import Annotated, Iterator, Self

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


def _expand(path: str) -> Path:
    return Path(path).expand()


CmdTemplate = Annotated[str, pd.AfterValidator(_validate_cmd_template)]
DirectoryPath = Annotated[pd.DirectoryPath, pd.BeforeValidator(_expand)]
RawTarsDirs = dict[str, list[str]]
TarsDirs = dict[DirectoryPath, list[DirectoryPath]]


class Config(pd.BaseModel, extra='forbid'):
    cmd_template: CmdTemplate = Template(COMMAND_TEMPLATE_DEFAULT)  # type: ignore
    root_dir: DirectoryPath = '/'  # type: ignore
    targets_dirs: TarsDirs

    @pd.field_validator('targets_dirs', mode='before')
    @classmethod
    def _(cls, targets_dirs: RawTarsDirs, info: pd.FieldValidationInfo) -> RawTarsDirs:
        targets_dirs = copy.deepcopy(targets_dirs)

        assert 'root_dir' in info.data, "'root_dir' is invalid"
        root_dir = info.data['root_dir']

        assert isinstance(targets_dirs, dict), "'targets_dirs' must be a table"
        for target, dirs in targets_dirs.items():
            assert isinstance(dirs, list), "'dirs' must be an array"
            targets_dirs[target] = [root_dir / _expand(dir_) for dir_ in dirs]

        return targets_dirs

    @classmethod
    def from_env_var(cls, env_var: str = _CONFIG_PATH_ENV_VAR) -> Self:
        return cls.from_path(_env_var_to_path(env_var))

    @classmethod
    def from_path(cls, path: Path) -> Self:
        try:
            return cls(**tomllib.loads(path.read_text()))
        except FileNotFoundError:
            raise ConfigNotFoundError(path)
        except tomllib.TOMLDecodeError as e:
            raise InvalidConfigError(path, str(e))
        except pd.ValidationError as e:
            raise InvalidConfigError.from_pydantic(path, e)

    def each_target_and_dir(self) -> Iterator[tuple[DirectoryPath, DirectoryPath]]:
        for target, dirs in self.targets_dirs.items():
            yield from itertools.product((target,), dirs)


def _env_var_to_path(env_var: str) -> Path:
    try:
        return Path(os.environ[env_var])
    except KeyError:
        raise ConfigEnvVarUnsetError(env_var)
