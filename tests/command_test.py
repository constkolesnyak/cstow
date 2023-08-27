import pytest

from cstow.command import InvalidCmdActionError, str_to_action
from tests.testing_utils import pyt_print


def test_bad_cmd_action() -> None:
    with pytest.raises(InvalidCmdActionError) as exc:
        str_to_action('asdfqwer')
    pyt_print(exc.value)
