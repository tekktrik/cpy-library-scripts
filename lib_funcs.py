# SPDX-FileCopyrightText: 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""

lib_funcs.py
============

Library-specific functionalities to aid in developing patches

"""

import os
import functools
from typing import TypeAlias, Protocol, Sequence, Any

# Helpful type annotation for path-like strings
StrPath: TypeAlias = str | os.PathLike[str]

# pylint: disable=too-few-public-methods
class LibraryFunc(Protocol):
    """Typing protocol for methods (or callables) that take the following
    parameters:

    - (StrPath) The path to a specific Adafruit library
    - (Sequence[Any]) A list of other arguments
    """

    def __call__(self, lib_path: StrPath, *args: Sequence[Any]) -> Any:
        ...


def with_lib_path(func: LibraryFunc) -> LibraryFunc:
    """Decorator for automating temporarily entering a function's
    library directory

    :param LibraryFunc func: The library function to decorate
    """

    @functools.wraps(func)
    def wrapper_use_lib_path(*args, **kwargs) -> Any:

        # Get the relevant directories
        current_path = os.getcwd()
        lib_path = args[0]

        # Enter the library directory for the duration of executing the function
        os.chdir(lib_path)
        result = func(*args, **kwargs)
        os.chdir(current_path)

        # Return the result of the function
        return result

    return wrapper_use_lib_path
