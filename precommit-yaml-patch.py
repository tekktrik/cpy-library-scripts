import time
import os
import subprocess
import glob
import parse
import oyaml
from oyaml import Loader, Dumper

# Current path
home_path = os.getcwd()

# Bundle branches
LIBRARY_BRANCHES = ("drivers", "helpers")
YAML_PATH_LOCAL = ".pre-commit-config.yaml"

# Loop through each bundle branch
for branch_name in LIBRARY_BRANCHES:

    libraries_glob_path = os.path.join("Adafruit_CircuitPython_Bundle", "libraries", branch_name, "*")
    libraries_path_list = glob.glob(libraries_glob_path)

    # Enter each library in the bundle
    for library_path in libraries_path_list:
        yaml_path = os.path.join(library_path, ".pre-commit-config.yaml")
        print(f"Now modifying {yaml_path}")

        try:

            os.chdir(library_path)
            #print(os.getcwd())
            os.popen("git fetch").read()
            os.popen("git pull origin main").read()
            os.popen("git checkout main").read()
            os.popen("git reset --hard main").read()

            #with open(YAML_PATH_LOCAL, mode="r", encoding="utf-8") as inputtxt:
            #    alllines = iter(inputtxt.readlines())
            #    somelines = []
            #    for _ in range(4):
            #            next(alllines)
            #    for line in alllines:
            #        somelines.append(line)

            #with open("temp-precommit.yaml", mode="w", encoding="utf-8") as outputtxt:
            #    outputtxt.writelines(somelines)

            # Open the pre-commit config YAML and load it
            #print(os.listdir(os.getcwd()))
            with open(YAML_PATH_LOCAL, mode="r", encoding="utf-8") as inputyaml:
                yaml_object = oyaml.load(inputyaml, Loader=Loader)
                yaml_repos = yaml_object["repos"]

            #os.remove("temp-precommit.yaml")

            # Make the modifications, some needed for a second pass-through
            # First, update reuse version
            for repo in yaml_repos:
                if repo["repo"] == "https://github.com/fsfe/reuse-tool":
                    repo["rev"] = "v0.14.0"
                    break

            # Next, update pre-commit-hooks version
            for repo in yaml_repos:
                if repo["repo"] == "https://github.com/pre-commit/pre-commit-hooks":
                    repo["rev"] = "v4.2.0"
                    break

            # Next, update pre-commit-hooks version
            for repo in yaml_repos:
                if repo["repo"] == "https://github.com/python/black":
                    repo["rev"] = "22.3.0"
                    break

            # Finally, some things get converted to YAML-style lists automatically
            # So, we'll manually edit them to make sure they don't actually change
            pylint_repo = [repo for repo in yaml_repos if repo["repo"] == "https://github.com/pycqa/pylint"][0]
            for hook in pylint_repo["hooks"]:
                if hook["types"] == ["python"]:
                    hook["types"] = "[python]"

                try:
                    hook["exclude"] = 'CHANGEME = "' + hook["exclude"] + '"'
                except KeyError:
                    pass

                try:
                    hook["files"] = 'CHANGEME = "' + hook["files"] + '"'
                except KeyError:
                    pass

            # Write the YAML file
            #with open(".pre-commit-config.yaml", mode="w", encoding="utf-8") as outputyaml:
            with open(YAML_PATH_LOCAL, mode="w", encoding="utf-8") as outputyaml:
                outputyaml.writelines([
                    "# SPDX-FileCopyrightText: 2020 Diego Elio Pettenò\n",
                    "#\n",
                    "# SPDX-License-Identifier: Unlicense\n",
                    "\n",
                ])
            with open(YAML_PATH_LOCAL, mode="a", encoding="utf-8") as outputyaml:
                oyaml.dump(yaml_object, outputyaml, Dumper=Dumper, indent=4)

            # Iterate through output file to fix spacing and the '[python]' issue
            #with open(".pre-commit-config.yaml", mode="r", encoding="utf-8") as inputfile:
            with open(YAML_PATH_LOCAL, mode="r", encoding="utf-8") as inputfile:
                yamlfile_lines = inputfile.readlines()

            modified_lines = []

            for line in yamlfile_lines:
                new_line = line
                if new_line.strip().startswith("-"):
                    new_line = new_line.replace("-  ", "  -", 1)
                if new_line.strip().startswith("- --"):
                    new_line = new_line.replace("- --", "  - --")
                if new_line.strip().startswith("types") and line.find("'[python]'") != -1:
                    new_line = new_line.replace("'[python]'", "[python]")
                if new_line.find("CHANGEME = ") != -1:
                    exclude_value = parse.parse('exclude: CHANGEME = "{}"', new_line.strip())
                    if exclude_value:
                        new_line = new_line.replace('CHANGEME = "' + exclude_value[0] + '"', '"' + exclude_value[0] + '"')
                    files_value = parse.parse('files: CHANGEME = "{}"', new_line.strip())
                    if files_value:
                        new_line = new_line.replace('CHANGEME = "' + files_value[0] + '"', '"' + files_value[0] + '"')
                modified_lines.append(new_line)

            # Write the fixed YAML file
            #with open(".pre-commit-config.yaml", mode="w", encoding="utf-8") as outputfile:
            with open(YAML_PATH_LOCAL, mode="w", encoding="utf-8") as outputfile:
                outputfile.writelines(modified_lines)

            # Submit the patch and open the 
            os.popen("git add -A").read()
            os.popen('git commit -m "Patch .pre-commit-config.yaml"').read()
            os.popen("git push").read()
            os.popen("git status").read()
            #os.popen("gh repo view --web")
            os.chdir(home_path)

            #input("Press Enter to continue...")
            #time.sleep(10)

        except FileNotFoundError:
            print(f".pre-commit-config.yaml not found for {library_path}")
