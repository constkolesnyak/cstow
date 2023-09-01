import pytest

from cstow.command import InvalidCmdActionError, str_to_action
from tests.utils import pytest_print


def test_bad_cmd_action() -> None:
    with pytest.raises(InvalidCmdActionError) as exc:
        str_to_action('asdfqwer')
    pytest_print(exc.value)
