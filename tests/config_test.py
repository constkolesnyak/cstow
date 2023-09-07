import os

import pytest
from path import Path

from cstow.command import CmdAction
from cstow.config import _CONFIG_PATH_ENV_VAR  # type: ignore
from cstow.config import (
    Config,
    ConfigEnvVarUnsetError,
    ConfigNotFoundError,
    InvalidConfigError,
)
from cstow.main import _cli  # type: ignore
from tests.utils import pytest_print

TESTING_DATA: Path = Path(__file__).parent / 'testing_data'
CONFIGS: Path = TESTING_DATA / 'configs'
DIR_FILE: Path = TESTING_DATA / 'dir' / 'file'
TARGET_SYMLINK: Path = TESTING_DATA / 'target' / 'file'

os.environ['CSTOW_TESTING_DATA'] = TESTING_DATA


def get_configs(glob: str) -> list[str]:
    """Get config filenames matching the glob."""
    return [cfg.name for cfg in CONFIGS.glob(glob)]


@pytest.mark.smoke
@pytest.mark.parametrize('good_config', get_configs('good_*'))
def test_good_configs(good_config: Path) -> None:
    os.environ[_CONFIG_PATH_ENV_VAR] = CONFIGS / good_config

    _cli(CmdAction.DELETE, plain=True)
    assert not TARGET_SYMLINK.exists()

    _cli(CmdAction.STOW)
    assert TARGET_SYMLINK.islink() and TARGET_SYMLINK.readlinkabs() == DIR_FILE


@pytest.mark.parametrize('bad_config', get_configs('bad_*'))
def test_bad_configs(bad_config: Path) -> None:
    os.environ[_CONFIG_PATH_ENV_VAR] = CONFIGS / bad_config

    with pytest.raises(InvalidConfigError) as exc:
        Config.from_env_var()
    pytest_print(exc.value)


def test_bad_env_var() -> None:
    os.environ[_CONFIG_PATH_ENV_VAR] = 'asdfqwerasdfqwerasdf'

    with pytest.raises(ConfigNotFoundError) as exc:
        Config.from_env_var()
    pytest_print(exc.value)


def test_unset_env_var() -> None:
    del os.environ[_CONFIG_PATH_ENV_VAR]

    with pytest.raises(ConfigEnvVarUnsetError) as exc:
        Config.from_env_var()
    pytest_print(exc.value)
