"""

status_checker.py
=================

Uses the `gh` CLI to check the status of repos contained within a
cloned Adafruit CircuitPython Bundle

* Author(s): Alec Delaney

"""

import os
import glob
import json
from typing import Optional, TypeAlias

# Helpful type annotation for path-like strings
StrPath: TypeAlias = str | os.PathLike[str]

# The Default path uses the current working directory
DEFAULT_BUNDLE_PATH = os.path.join(os.getcwd(), "Adafruit_CircuitPython_Bundle")


def _run_gh_cli_check(
    user: Optional[str] = None,
    workflow_name: Optional[str] = "Build CI",
) -> bool:
    """Runs the `gh` CLI in the current working directory

    :param str|None user: The user that triggered the run; if `None` is
        provided, any user is acceptable
    :param str|None workflow_name: The name of the workflow; if `None` is
        provided, any workflow name is acceptable; the defail is
        `"Build CI"`
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
    return latest_result["conclusion"] != "success"


# pylint: disable=too-many-nested-blocks
def check_build_statuses(
    bundle_path: StrPath = DEFAULT_BUNDLE_PATH,
    user: Optional[str] = None,
    workflow_name: Optional[str] = "Build CI",
    *,
    debug: bool = False,
) -> tuple[list[str], list[str]]:
    """Uses the `gh` CLI client to check the build statuses of the Adafruit
    CircuitPython Bundle

    :param StrPath bundle_path: The path to the Adafruit CircuitPython
        Bundle; the default assumes its in the current working directory
    :param str|None user: The user that triggered the run; if `None` is
        provided, any user is acceptable
    :param str|None workflow_name: The name of the workflow; if `None` is
        provided, any workflow name is acceptable; the defail is
        `"Build CI"`
    :param bool debug: (keyword-only) Whether debug statements should be
        printed to the standard output
    """

    # Bundle branches
    library_branches = ("drivers", "helpers")

    # Get home path to return to after each change
    home_path = os.path.dirname(os.path.abspath(bundle_path))

    # Initialize list of failed/errored patches
    failed_builds = []
    error_builds = []

    # Loop through each bundle branch
    for branch_name in library_branches:

        libraries_glob_path = os.path.join(bundle_path, "libraries", branch_name, "*")
        libraries_path_list = glob.glob(libraries_glob_path)

        # Enter each library in the bundle
        for library_path in libraries_path_list:
            os.chdir(library_path)
            if debug:
                print(f"Now checking {library_path}")

            suspect_lib = "".join([branch_name, "/", os.path.basename(library_path)])

            try:
                # Run through `gh` CLI check, handle failures
                if _run_gh_cli_check(user, workflow_name):
                    if debug:
                        print("***", "Library", suspect_lib, "failed the patch!", "***")
                    failed_builds.append(suspect_lib)

            except json.decoder.JSONDecodeError:
                # Handle that an error occured using the `gh` CLI
                if debug:
                    print(
                        "???",
                        "Library",
                        suspect_lib,
                        "had an error occur, could not be determined",
                        "???",
                    )
                error_builds.append(suspect_lib)

            finally:
                # Change back to home directory
                os.chdir(home_path)

    return failed_builds, error_builds


def save_build_statuses(
    failed_builds: Optional[list[str]] = None,
    error_builds: Optional[list[str]] = None,
    failure_filepath: StrPath = "failures.txt",
    error_filepath: StrPath = "errors.txt",
):
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
