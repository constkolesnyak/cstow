import shlex
from enum import StrEnum, auto
from string import Template
from typing import Iterator

import attrs


class CmdAction(StrEnum):
    NO = auto()
    RESTOW = auto()
    DELETE = auto()


class InvalidActionError(Exception):
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
            raise InvalidActionError(action)

    @classmethod
    def fields(cls) -> Iterator[str]:
        return map(lambda field: field.name, attrs.fields(cls))  # todo attrgetter

    def cmd(self, template: Template) -> str:
        return template.substitute(
            **{attr: shlex.quote(val) for attr, val in vars(self).items()}
        )


COMMAND_TEMPLATE_DEFAULT: str = (
    "stow --${} --no-folding --verbose -d ${} -t ${} . 2>&1 | grep -v -e '^BUG' -e '^WARN'"
).format(*CmdVars.fields())
