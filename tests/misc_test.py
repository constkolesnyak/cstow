import pytest

from cstow.command import CmdVars, InvalidCmdActionError
from tests.testing_utils import pyt_print


def test_bad_cmd_action() -> None:
    with pytest.raises(InvalidCmdActionError) as exc:
        CmdVars('asdfqwer', '', '')  # type: ignore
    pyt_print(exc.value)
