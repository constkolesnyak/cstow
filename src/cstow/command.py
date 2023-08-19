import shlex
from enum import StrEnum, auto
from operator import attrgetter
from string import Template
from typing import Iterator

import attrs


class CmdAction(StrEnum):
    NO = auto()
    STOW = auto()
    RESTOW = auto()
    DELETE = auto()


class InvalidCmdActionError(Exception):
    def __init__(self, action: str) -> None:
        super().__init__(
            f"Action '{action}' is invalid\nUse one of these: " + ', '.join(CmdAction)
        )


@attrs.define(slots=False)
class CmdVars:
    action: str = attrs.field()
    directory: str
    target: str

    @action.validator  # type: ignore
    def _(self, attr, action: CmdAction) -> None:  # type: ignore
        if action not in list(CmdAction):
            raise InvalidCmdActionError(action)

    @classmethod
    def fields(cls) -> Iterator[str]:
        return map(attrgetter('name'), attrs.fields(cls))

    def cmd(self, template: Template) -> str:
        return template.substitute(
            **{attr: shlex.quote(val) for attr, val in vars(self).items()}
        )


COMMAND_TEMPLATE_DEFAULT: str = (
    "stow --${} --no-folding --verbose -d ${} -t ${} . 2>&1 | grep -v -e '^BUG' -e '^WARN'"
).format(*CmdVars.fields())
