# SPDX-FileCopyrightText: 2022 Alec Delaney
#
# SPDX-License-Identifier: MIT

"""

status_checker_example.py
=========================

Script that uses the `gh` CLI to check on the build status of libraries
in the Adafruit_CircuitPython_Bundle, and saves the failures and errors
to text files

* Author(s): Alec Delaney

"""

import os
from cpy_scripts.build_status import check_build_statuses, save_build_statuses

bundle_path = os.path.join(os.getcwd(), "Adafruit_CircuitPython_Bundle")

build_results = check_build_statuses(bundle_path, user="tekktrik", debug=True)
save_build_statuses(build_results)
