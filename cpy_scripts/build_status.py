# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""

build_status.py
===============

Functionality using the `gh` CLI to check the CI status of repos
contained within a cloned Adafruit CircuitPython Bundle

* Author(s): Alec Delaney

"""

import os
import json
from typing import Optional, Literal, List, Tuple
from cpy_scripts.base.lib_funcs import StrPath, in_lib_path
from cpy_scripts.base.iter_libraries import iter_library_with_func

# The Default path uses the current working directory
DEFAULT_BUNDLE_PATH: str = os.path.join(os.getcwd(), "Adafruit_CircuitPython_Bundle")
"""The default assumed path to the bundle, which is that it is within the
current working directory"""


def run_gh_cli_check(
    user: Optional[str] = None,
    workflow_name: Optional[str] = "Build CI",
) -> bool:
    """Runs the `gh` CLI in the current working directory

    :param str|None user: The user that triggered the run; if `None` is
        provided, any user is acceptable
    :param str|None workflow_name: The name of the workflow; if `None` is
        provided, any workflow name is acceptable; the defail is
        `"Build CI"`
    :return: Whether the requested build was successful
    :rtype: bool
    """

    # Prepare the `gh` command
    gh_cmd = ["gh run list"]
    if user:
        gh_cmd.append(f"-u {user}")
    if workflow_name:
        gh_cmd.append(f'-w "{workflow_name}"')
    gh_cmd.append("--json conclusion")

    # Use the prepared command with the `gh` CLI
    gh_cmd = " ".join(gh_cmd)
    proc_result = os.popen(gh_cmd).read()
    results = json.loads(proc_result)
    latest_result = results[0]

    # Return the results
    return latest_result["conclusion"] == "success"


@in_lib_path
def check_build_status(
    lib_path: StrPath,
    user: Optional[str] = None,
    workflow_name: Optional[str] = "Build CI",
    debug: bool = False,
) -> Literal["Success", "Failed", "Error"]:
    """Uses the `gh` CLI client to check the build statuses of the Adafruit
    CircuitPython Bundle

    :param StrPath lib_path: The path to the Adafruit library
    :param str|None user: The user that triggered the run; if `None` is
        provided, any user is acceptable
    :param str|None workflow_name: The name of the workflow; if `None` is
        provided, any workflow name is acceptable; the defail is
        `"Build CI"`
    :param bool debug: Whether debug statements should be printed to
        the standard output
    :return: Whether the requested build was successful, failed, or had
        and error occur during the check
    :rtype: str
    """

    if debug:
        print("Checking", lib_path)

    try:
        # Run through `gh` CLI check, handle failures
        if run_gh_cli_check(user, workflow_name):
            return "Success"
        if debug:
            print("***", "Library", lib_path, "failed the patch!", "***")
        return "Failed"

    except json.decoder.JSONDecodeError:
        # Handle that an error occured using the `gh` CLI
        if debug:
            print(
                "???",
                "Library",
                lib_path,
                "had an error occur, could not be determined",
                "???",
            )
        return "Error"


def check_build_statuses(
    bundle_path: StrPath,
    user: Optional[str] = None,
    workflow_name: Optional[str] = "Build CI",
    debug: bool = False,
) -> List[Tuple[StrPath, Literal["Success", "Failed", "Error"]]]:
    """Checks all the libraries in a cloned Adafruit CircuitPython Bundle
    to get the latest build status with the requested infomration

    :param StrPath bundle_oath: The path to the cloned bundle
    :param str|None user: The user that triggered the run; if `None` is
        provided, any user is acceptable
    :param str|None workflow_name: The name of the workflow; if `None` is
        provided, any workflow name is acceptable; the defail is
        `"Build CI"`
    :param bool debug: Whether debug statements should be printed to
        the standard output
    :return: A list of tuples containing paired library paths and build
        statuses
    :rtype: list
    """

    args = (user, workflow_name, debug)
    return iter_library_with_func(bundle_path, [(check_build_status, args)])


def save_build_statuses(
    build_results: List[Tuple[StrPath, Literal["Success", "Failed", "Error"]]],
    failure_filepath: StrPath = "failures.txt",
    error_filepath: StrPath = "errors.txt",
) -> None:
    """Save the list of failed and/or errored libraries to files

    :param list[str]|None failed_builds: The list of failed libraries; if
        `None` is provided, it will not create a file for this
    :param list[str]|None error_builds: The list of libraries that had errors
        during the `gh` CLI check; if `None` is provided, it will not create
        a file for this
    :param StrPath failure_filepath: The filename/filepath to write the list
        of failed libraries to; the default is "failures.txt"
    :param StrPath error_filepath: The filename/filepath to write the list
        of libraries with errored checks to; the default is "errors.txt"
    """

    # Get failed and errored builds
    failed_builds = [result[0] for result in build_results if result[1] == "Failed"]
    error_builds = [result[0] for result in build_results if result[1] == "Error"]

    # Save the list of failed builds, if provided
    if failed_builds:
        with open(failure_filepath, mode="w", encoding="utf-8") as outputfile:
            for build in failed_builds:
                outputfile.write(build + "\n")

    # Save the list of errored builds, if provided
    if error_builds:
        with open(error_filepath, mode="w", encoding="utf-8") as outputfile:
            for build in error_builds:
                outputfile.write(build + "\n")
