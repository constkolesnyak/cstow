import os

import pytest
from dotenv import load_dotenv
from path import Path

from cstow.command import CmdAction
from cstow.config import _CONFIG_PATH_ENV_VAR  # type: ignore
from cstow.main import _cli  # type: ignore

load_dotenv()

TESTING_DATA: Path = Path(__file__).parent / 'testing_data'
CONFIGS: Path = TESTING_DATA / 'configs'
DIR_FILE: Path = TESTING_DATA / 'dir' / 'file'
TARGET_SYMLINK: Path = TESTING_DATA / 'target' / 'file'


@pytest.mark.smoke
def test_good_configs() -> None:
    for good_config in CONFIGS.glob('good_*'):
        os.environ[_CONFIG_PATH_ENV_VAR] = good_config
        TARGET_SYMLINK.remove_p()
        _cli(CmdAction.STOW)
        assert TARGET_SYMLINK.islink() and TARGET_SYMLINK.readlinkabs() == DIR_FILE


def test_bad_configs():
    ...
