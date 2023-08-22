import shlex
from enum import StrEnum, auto
from string import Template
from typing import Iterator

import attrs
from path import Path


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
    action: CmdAction
    target: Path
    dir: Path

    @action.validator  # type: ignore
    def _(self, _, action: CmdAction) -> None:
        if action not in list(CmdAction):
            raise InvalidCmdActionError(action)

    @classmethod
    def fields(cls) -> Iterator[str]:
        return (field.name for field in attrs.fields(cls))

    def cmd(self, template: Template) -> str:
        return template.substitute(
            **{field: shlex.quote(str(val)) for field, val in vars(self).items()}
        )


COMMAND_TEMPLATE_DEFAULT: str = (
    "stow --${} --no-folding --verbose -t ${} -d ${} . 2>&1 | grep -v -e '^BUG' -e '^WARN'"
).format(*CmdVars.fields())
