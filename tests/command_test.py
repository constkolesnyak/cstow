import pytest

from cstow.command import CmdAction, InvalidCmdActionError
from tests.utils import pytest_print


def test_bad_cmd_action() -> None:
    with pytest.raises(InvalidCmdActionError) as exc:
        CmdAction.from_str('asdfqwer')
    pytest_print(exc.value)
