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
from typing import TypeAlias, Tuple, Iterable, Any, List, Sequence, Dict
from cpy_scripts.lib_funcs import StrPath, LibFunc

# Helpful type annotation definitions

LibFunc_IterInstruction: TypeAlias = Tuple[LibFunc, Sequence[Any], Dict[str, Any]]
"""Instruction set as a tuple of a function to run on a library,
a list of the positional arguments to be provided to it, and a
dictionary of keyword arguments to be provided to it"""

LibFunc_IterResult: TypeAlias = Tuple[StrPath, List[Any]]
"""Result of function(s) run on a library as a tuple of the
path to the library modified and a list of the result(s) of
the function(s)"""


def iter_library_with_func(
    bundle_path: StrPath,
    func_workflow: Iterable[LibFunc_IterInstruction],
) -> List[LibFunc_IterResult]:
    """Iterate through the libraries and run a given function with the
    provided arguments

    :param StrPath bundle_path: The path to the cloned bundle
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

    # Initialize list of results
    results = []

    # Loop through each bundle branch
    for branch_name in library_branches:

        libraries_glob_path = os.path.join(bundle_path, "libraries", branch_name, "*")
        libraries_path_list = glob.glob(libraries_glob_path)

        # Enter each library in the bundle
        for library_path in libraries_path_list:

            func_results = []

            for func, args, kwargs in func_workflow:
                result = func(library_path, *args, **kwargs)
                func_results.append(result)

            results.append((library_path, func_results))

    return results
