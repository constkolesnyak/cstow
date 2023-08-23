from typing import Any


def pyt_print(*args: Any, **kwargs: Any) -> None:
    print('\n')
    print(*args, **kwargs)
    print()
