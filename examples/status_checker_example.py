# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
from build_status import check_build_statuses, save_build_statuses

bundle_path = os.path.join(os.getcwd(), "Adafruit_CircuitPython_Bundle")

build_results = check_build_statuses(bundle_path, user="tekktrik", debug=True)
save_build_statuses(build_results)
