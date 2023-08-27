import dataclasses as dc
import shlex
from enum import StrEnum, auto
from string import Template
from typing import Iterator

from path import Path


class CmdAction(StrEnum):
    '''GNU Stow actions.'''

    NO = auto()
    STOW = auto()
    RESTOW = auto()
    DELETE = auto()


class InvalidCmdActionError(Exception):
    def __init__(self, action: str) -> None:
        super().__init__(
            f"Action '{action}' is invalid\nUse one of these: " + ', '.join(CmdAction)
        )


def str_to_action(action: str) -> CmdAction:
    '''
    Validate a GNU Stow action.

    Raises:
        InvalidCmdActionError: If the GNU Stow action is invalid.
    '''
    if action in list(CmdAction):
        return CmdAction(action)
    raise InvalidCmdActionError(action)


@dc.dataclass(frozen=True)
class CmdVars:
    '''
    Variables for constructing GNU Stow commands from a template.

    Attributes:
        action: A GNU Stow action.
        target: A target directory.
        dir: A source directory.
    '''

    action: CmdAction
    target: Path
    dir: Path

    @classmethod
    def fields(cls) -> Iterator[str]:
        return (field.name for field in dc.fields(cls))

    def cmd(self, template: Template) -> str:
        '''Construct a GNU Stow command from a template.'''
        return template.substitute(
            **{field: shlex.quote(str(val)) for field, val in vars(self).items()}
        )
