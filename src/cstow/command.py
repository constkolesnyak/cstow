import dataclasses as dc
import shlex
from enum import StrEnum, auto
from string import Template
from typing import Iterator

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


@dc.dataclass
class CmdVars:
    action: CmdAction
    target: Path
    dir: Path

    def __post_init__(self) -> None:
        if self.action not in list(CmdAction):
            raise InvalidCmdActionError(self.action)

    @classmethod
    def fields(cls) -> Iterator[str]:
        return (field.name for field in dc.fields(cls))

    def cmd(self, template: Template) -> str:
        return template.substitute(
            **{field: shlex.quote(str(val)) for field, val in vars(self).items()}
        )
