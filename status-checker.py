import os
import glob
import json

# Bundle branches
LIBRARY_BRANCHES = ("drivers", "helpers")

# Current path
home_path = os.getcwd()

# List of failed patches
failed_patches = []

# Loop through each bundle branch
for branch_name in LIBRARY_BRANCHES:

    libraries_glob_path = os.path.join("Adafruit_CircuitPython_Bundle", "libraries", branch_name, "*")
    libraries_path_list = glob.glob(libraries_glob_path)

    # Enter each library in the bundle
    for library_path in libraries_path_list:
        os.chdir(library_path)
        print(f"Now checking {library_path}")

        suspect_lib = "".join([branch_name, "/", os.path.basename(library_path)])

        try:
            # Get information using `gh`
            # Edit the below gh command as needed
            proc_result = os.popen('gh run list -w "Build CI" --json status,conclusion,name,createdAt,url').read()
            results = json.loads(proc_result)
            latest_result = results[0]

            # Check if latest build failed
            if latest_result["conclusion"] != "success":
                print("***", "Library", suspect_lib, "failed the patch!", "***")
                failed_patches.append(suspect_lib)
        
        except:
            # Record that an error occured
            print("???", "Library", suspect_lib, "had an error occur", "???")
            failed_patches.append("???" + suspect_lib + "???")

        finally:
            # Change back to home directory
            os.chdir(home_path)

with open("failed_statuses.txt", mode="w", encoding="utf-8") as outputfile:
    for patch in failed_patches:
        outputfile.write(patch + "\n")
