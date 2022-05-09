import os
import glob
import parse
import oyaml
from oyaml import Loader, Dumper

# Possible YAML filenames

# Bundle branches
LIBRARY_BRANCHES = ("drivers", "helpers")

# Loop through each bundle branch
for branch_name in LIBRARY_BRANCHES:

    libraries_glob_path = os.path.join("Adafruit_CircuitPython_Bundle", "libraries", branch_name, "*")
    libraries_path_list = glob.glob(libraries_glob_path)

    # Enter each library in the bundle
    for library_path in libraries_path_list:
        yaml_path = os.path.join(library_path, ".pre-commit-config.yaml")
        print(f"Now modifying {yaml_path}")

        try:
            # Open the pre-commit config YAML and load it
            with open(yaml_path, mode="r", encoding="utf-8") as inputyaml:
                yaml_object = oyaml.load(inputyaml, Loader=Loader)
                yaml_repos = yaml_object["repos"]

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
                

            print(yaml_repos)

            # Write the YAML file
            with open(".pre-commit-config.yaml", mode="w", encoding="utf-8") as outputyaml:
            #with open(yaml_path, mode="w", encoding="utf-8") as outputyaml:
                oyaml.dump(yaml_object, outputyaml, Dumper=Dumper, indent=4)

            #break

            # Iterate through output file to fix spacing and the '[python]' issue
            with open(".pre-commit-config.yaml", mode="r", encoding="utf-8") as inputfile:
            #with open(yaml_path, mode="r", encoding="utf-8") as inputfile:
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
                    print("YES")
                    print(new_line)
                    exclude_value = parse.parse('exclude: CHANGEME = "{}"', new_line.strip())
                    if exclude_value:
                        new_line = new_line.replace('CHANGEME = "' + exclude_value[0] + '"', '"' + exclude_value[0] + '"')
                    files_value = parse.parse('files: CHANGEME = "{}"', new_line.strip())
                    if files_value:
                        new_line = new_line.replace('CHANGEME = "' + files_value[0] + '"', '"' + files_value[0] + '"')
                modified_lines.append(new_line)

            # Write the fixed YAML file
            with open(".pre-commit-config.yaml", mode="w", encoding="utf-8") as outputfile:
            #with open(yaml_path, mode="w", encoding="utf-8") as outputfile:
                outputfile.writelines(modified_lines)

            break

        except FileNotFoundError:
            print(f".pre-commit-config.yaml not found for {library_path}")

    break
