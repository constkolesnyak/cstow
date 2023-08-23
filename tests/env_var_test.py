import os

import pytest

from cstow.config import _CONFIG_PATH_ENV_VAR  # type: ignore
from cstow.config import Config, ConfigEnvVarUnsetError, ConfigNotFoundError
from tests.testing_utils import pyt_print


def test_bad_env_var() -> None:
    os.environ[_CONFIG_PATH_ENV_VAR] = 'asdfqwerasdfqwerasdf'

    with pytest.raises(ConfigNotFoundError) as exc:
        Config.from_env_var()
    pyt_print(exc.value)


def test_unset_env_var() -> None:
    del os.environ[_CONFIG_PATH_ENV_VAR]

    with pytest.raises(ConfigEnvVarUnsetError) as exc:
        Config.from_env_var()
    pyt_print(exc.value)
