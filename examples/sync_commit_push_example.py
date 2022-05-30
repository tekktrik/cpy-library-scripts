# SPDX-FileCopyrightText: 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""

sync_commit_push_example.py
===========================

Script that uses ``git_funcs`` functionality to sync a remote repository
to the origin, commit any changes, and push them back to the remote

* Author(s): Alec Delaney

"""

import os
from cpy_scripts.git_funcs import sync_commit_push

# Create a LibFunc function to decorate. The branch name must exist
# in both the local repo as well as the remote, otherwise this will
# fail.
@sync_commit_push(message="More, I guess!", branch_name="the-new-branch")
def add_text_file(lib_path: str):
    """Simple function to add a new text file"""

    # Create a new file with some text
    text_filepath = os.path.join(lib_path, "new_file.txt")
    with open(text_filepath, mode="w", encoding="utf-8") as textfile:
        textfile.write("huehuehue\n")


# Run the decorated function
LIBPATH = "/home/tekktrik/Documents/Repositories/CircuitPython_TicStepper/"
add_text_file(LIBPATH)
