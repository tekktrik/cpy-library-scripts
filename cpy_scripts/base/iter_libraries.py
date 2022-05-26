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
from typing import Tuple, Iterable, Any, List, Sequence
from scripts.base.lib_funcs import StrPath, LibraryFunc


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

    # Initialize list of results
    results = []

    # Loop through each bundle branch
    for branch_name in library_branches:

        libraries_glob_path = os.path.join(bundle_path, "libraries", branch_name, "*")
        libraries_path_list = glob.glob(libraries_glob_path)

        # Enter each library in the bundle
        for library_path in libraries_path_list:

            func_results = []

            for func, args in func_workflow:
                result = func(library_path, *args)
                func_results.append(result)

            results.append((library_path, func_results))

    return results
