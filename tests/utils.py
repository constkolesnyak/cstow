from typing import Any


def pytest_print(*args: Any, **kwargs: Any) -> None:
    print('\n')
    print(*args, **kwargs)
    print()
