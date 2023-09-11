import dataclasses as dc
import shlex
from enum import StrEnum, auto
from string import Template
from typing import Iterator, Self

from path import Path


class InvalidCmdActionError(Exception):
    def __init__(self, action: str) -> None:
        super().__init__(
            f"Action '{action}' is invalid\nUse one of these: " + ", ".join(CmdAction)
        )


class CmdAction(StrEnum):
    """GNU Stow actions."""

    NO = auto()
    STOW = auto()
    RESTOW = auto()
    DELETE = auto()

    @classmethod
    def from_str(cls, action: str) -> Self:
        """
        Raises:
            InvalidCmdActionError: If the GNU Stow action is invalid.
        """
        if action in list(cls):
            return cls(action)
        raise InvalidCmdActionError(action)


@dc.dataclass(frozen=True)
class CmdPlaceholders:
    """
    Placeholders for constructing GNU Stow commands from a template.

    Attributes:
        action: A GNU Stow action.
        target: A target directory.
        dir: A stow directory.
    """

    action: CmdAction
    target: Path
    dir: Path

    @classmethod
    def fields(cls) -> Iterator[str]:
        return (field.name for field in dc.fields(cls))

    def cmd(self, template: Template) -> str:
        """Construct a GNU Stow command from a template."""
        return template.substitute(
            **{field: shlex.quote(str(val)) for field, val in vars(self).items()}
        )
