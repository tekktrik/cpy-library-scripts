# SPDX-FileCopyrightText: 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT


"""

iter_libraries.py
=================

Functionality for iterating through a cloned Adafruit CircuitPython
Bundle to run functions on each library

* Author(s): Alec Delaney

"""

import os
import glob
from typing import Tuple, TypeAlias, Iterable, Any, List, Sequence, Protocol

# Helpful type annotation for path-like strings
StrPath: TypeAlias = str | os.PathLike[str]

# Helpful type annotations for library iteration
# pylint: disable=too-few-public-methods
class LibraryFunc(Protocol):
    """Typing protocol for methods (or callables) that take the following
    parameters:

    - (StrPath) The path to a specific Adafruit library
    - (Sequence[Any]) A list of other arguments
    """

    def __call__(self, lib_path: StrPath, *args: Sequence[Any]) -> Any:
        ...


def iter_library_with_func(
    bundle_path: StrPath,
    func_workflow: Iterable[Tuple[LibraryFunc, Sequence[Any]]],
) -> List[Tuple[StrPath, List[Any]]]:
    """Iterate through the libraries and run a given function with the
    provided arguments

    :param StrPath bundle_oath: The path to the cloned bundle
    :param Iterable func_workflow: An iterable of tuples containing pairs
        of functions and corresponding arguments; the path to each specific
        library is automatically provided to the functions, so the functions
        must account for it
    :return: A list containing tuples of pairs of each library path and a list
        with the results from each function
    :rtype: list
    """

    # Bundle branches
    library_branches = ("drivers", "helpers")

    # Get home path to return to after each change
    home_path = os.path.dirname(os.path.abspath(bundle_path))

    # Initialize list of results
    results = []

    # Loop through each bundle branch
    for branch_name in library_branches:

        libraries_glob_path = os.path.join(bundle_path, "libraries", branch_name, "*")
        libraries_path_list = glob.glob(libraries_glob_path)

        # Enter each library in the bundle
        for library_path in libraries_path_list:
            os.chdir(library_path)

            func_results = []

            for func, args in func_workflow:
                result = func(library_path, *args)
                func_results.append(result)

            results.append((library_path, func_results))

            os.chdir(home_path)

    return results
