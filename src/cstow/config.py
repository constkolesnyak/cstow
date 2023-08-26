'''
Usage example:

    try:
        config: Config = Config.from_env_var()
        ...
    except ConfigError as e:
        ...
'''

import copy
import itertools
import os
import tomllib
from abc import ABC
from string import Template
from typing import Annotated, Iterator, Self

import pydantic as pd
from path import Path

from cstow.command import CmdVars

_CONFIG_PATH_ENV_VAR = 'CSTOW_CONFIG_PATH'

_CMD_TEMPLATE_DEFAULT = Template(
    "stow --${} --no-folding --verbose -t ${} -d ${} . ".format(*CmdVars.fields())
    + "2>&1 | grep -v -e '^BUG' -e '^WARN'"  # Clean output
)
_ROOT_DIR_DEFAULT = Path('/')


class ConfigError(ABC, Exception):
    '''Any error with a user config.'''


class ConfigEnvVarUnsetError(ConfigError):
    def __init__(self, env_var: str) -> None:
        super().__init__(
            f'Environment variable {env_var} is unset. Expected path to cstow_config.toml'
        )


class ConfigNotFoundError(ConfigError):
    def __init__(self, path: str) -> None:
        super().__init__(f'No such file: {path}\nExpected path to cstow_config.toml')


class InvalidConfigError(ConfigError):
    def __init__(self, path: str, message: str) -> None:
        super().__init__(f'Invalid config: {path}\n\n{message}')

    @classmethod
    def from_pydantic(cls, path: str, exception: pd.ValidationError) -> Self:
        '''Convert a Pydantic error message to an even more user-friendly one.'''
        messages: list[str] = []

        for err in exception.errors():
            loc = err['loc'][0]
            inp = err['input']
            msg = err['msg'].lstrip('Assertion failed, ')
            messages.append(f'{loc}\n    input: {inp}\n    error: {msg}')

        return cls(path, '\n\n'.join(messages))


def _validate_cmd_template(template_str: str) -> Template:
    '''Use with Pydantic and typing.Annotated.'''
    cmd_template = Template(template_str)

    assert cmd_template.is_valid(), "Invalid syntax in 'cmd_template'"
    assert set(cmd_template.get_identifiers()) == set(
        CmdVars.fields()
    ), f"'cmd_template' must contain all of these vars and no others: " + ", ".join(
        CmdVars.fields()
    )

    return cmd_template


def _expand(path: str) -> Path:
    return Path(path).expand()


CmdTemplate = Annotated[str, pd.AfterValidator(_validate_cmd_template)]
DirectoryPath = Annotated[pd.DirectoryPath, pd.BeforeValidator(_expand)]
TarsDirs = dict[DirectoryPath, list[pd.DirectoryPath]]


class Config(pd.BaseModel, extra='forbid'):
    '''
    The user config validated by Pydantic.

    Attributes:
        cmd_template: A template for constructing GNU Stow commands.
        root_dir: The root directory of source directories.
        targets_dirs: A dictionary of target directories and associated source directories.

    Raises:
        pydantic.ValidationError: If the config is invalid.
    '''

    cmd_template: CmdTemplate = _CMD_TEMPLATE_DEFAULT  # type: ignore
    root_dir: DirectoryPath = _ROOT_DIR_DEFAULT  # type: ignore
    targets_dirs: TarsDirs

    @pd.field_validator('targets_dirs', mode='before')
    @classmethod
    def _(
        cls, targets_dirs: dict[str, list[str]], info: pd.FieldValidationInfo
    ) -> dict[str, list[Path]]:
        '''Expand dirs in targets_dirs and prefix them with the root_dir.'''
        targets_dirs = copy.deepcopy(targets_dirs)

        assert 'root_dir' in info.data, "'root_dir' is invalid"
        root_dir = info.data['root_dir']

        assert isinstance(targets_dirs, dict), "'targets_dirs' must be a table"
        for target, dirs in targets_dirs.items():
            assert isinstance(dirs, list), "'dirs' must be an array"
            targets_dirs[target] = [root_dir / _expand(dir_) for dir_ in dirs]

        return targets_dirs  # type: ignore

    @classmethod
    def from_env_var(cls, env_var: str = _CONFIG_PATH_ENV_VAR) -> Self:
        '''
        Load a user config from a file provided by an environment variable.

        Args:
            env_var:
                An environment variable pointing to a user config file.
                Defaults to _CONFIG_PATH_ENV_VAR.

        Raises:
            ConfigEnvVarUnsetError: If the environment variable is unset.
            ConfigNotFoundError: If the file is not found.
            InvalidConfigError: If the config is invalid.
        '''
        return cls.from_path(_env_var_to_path(env_var))

    @classmethod
    def from_path(cls, path: Path) -> Self:
        '''
        Load a user config from a file.

        Args:
            path: A path to a user config file.

        Raises:
            ConfigNotFoundError: If the file is not found.
            InvalidConfigError: If the config is invalid.
        '''
        try:
            return cls(**tomllib.loads(path.read_text()))
        except FileNotFoundError:
            raise ConfigNotFoundError(path)
        except tomllib.TOMLDecodeError as e:
            raise InvalidConfigError(path, str(e))
        except pd.ValidationError as e:
            raise InvalidConfigError.from_pydantic(path, e)

    def each_target_and_dir(self) -> Iterator[tuple[DirectoryPath, DirectoryPath]]:
        '''
        Iterate over targets_dirs.

        Yields:
            Every pair of a target directory and a source directory.
        '''
        for target, dirs in self.targets_dirs.items():
            yield from itertools.product((target,), dirs)


def _env_var_to_path(env_var: str) -> Path:
    try:
        return Path(os.environ[env_var])
    except KeyError:
        raise ConfigEnvVarUnsetError(env_var)
