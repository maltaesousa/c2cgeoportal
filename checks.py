import configparser
import glob
import os
import subprocess
import sys

import magic  # python-magic
import yaml
from editorconfig import EditorConfigError, get_properties  # editorconfig


def check_black_config():
    python = False
    try:
        next(glob.iglob("**/.py", recursive=True))
        python = True
    except StopIteration:
        pass

    try:
        for file_ in glob.iglob("**/*[0-9a-zA-z_-][0-9a-zA-z_-][0-9a-zA-z_-]", recursive=True):
            if os.path.isfile(file_):
                if magic.from_file(file_, mime=True) == "text/x-python":
                    python = True
                    break
    except StopIteration:
        pass

    if python:
        if not os.path.exists("pyproject.toml"):
            print("The file pyproject.toml with a section tool.black is required")
            return 1

        configp = configparser.ConfigParser()
        configp.read("pyproject.toml")
        if "tool.black" not in configp.sections():
            print("The tool.black section is required in the pyproject.toml file")
            return 1
    return 0


STANADARD_PROPERTIES = {
    "end_of_line": "lf",
    "insert_final_newline": "true",
    "charset": "utf-8",
    "indent_style": "space",
    "trim_trailing_whitespace": "true",
    "max_line_length": "110",
    "quote_type": "single",
}
PROPERTIES_2 = dict(STANADARD_PROPERTIES)
PROPERTIES_4 = dict(STANADARD_PROPERTIES)
PROPERTIES_2["indent_size"] = "2"
PROPERTIES_4["indent_size"] = "4"
PROPERTIES_MK = dict(PROPERTIES_4)
PROPERTIES_MK["indent_style"] = "tab"
PROPOERTIES = {
    "*.py": PROPERTIES_4,
    "*.yaml": PROPERTIES_2,
    "*.json": STANADARD_PROPERTIES,
    "*.java": PROPERTIES_4,
    "*.js": PROPERTIES_2,
    "*.mk": PROPERTIES_MK,
    "*.MAKEFILE": PROPERTIES_MK,
}


def check_editorconfig():
    code = 0
    for patern, wanted_properties in PROPOERTIES.items():
        try:
            file_ = next(glob.iglob("**/" + patern, recursive=True))
            properties = get_properties(os.path.abspath(file_))

            for key, value in wanted_properties.items():
                if value != None and properties[key] != value:
                    print(
                        "For pattern: {} the property '{}' is '{}' but should be '{}'.".format(
                            patern, key, properties[key], value
                        )
                    )
                    code = 1
        except StopIteration:
            pass
        except EditorConfigError:
            print("Error occurred while getting EditorConfig properties")
            return 1
    return code


def check_gitattribute():
    try:
        git_ref = (
            subprocess.check_output(["git", "--no-pager", "log", "--oneline"])
            .decode()
            .strip()
            .split("\n")[-1]
            .split(" ")[0]
        )
        print(git_ref)
        subprocess.check_call(["git", "--no-pager", "diff", "--check", git_ref])
        return 0
    except subprocess.CalledProcessError:
        return 1


FNULL = open(os.devnull, "w")


def check_eof():
    try:
        code = 0

        for filename in subprocess.check_output(["git", "ls-files"]).decode().split("\n"):
            if os.path.isfile(filename):
                if (
                    subprocess.call(
                        "git check-attr -a '{}' | grep ' text: set'".format(filename),
                        shell=True,
                        stdout=FNULL,
                    )
                    == 0
                ):
                    size = os.stat(filename).st_size
                    if size != 0:
                        with open(filename) as f:
                            f.seek(size - 1)
                            if ord(f.read()) != ord("\n"):
                                print("No new line at end of '{}' file.".format(filename))
                                code = 1

        return code
    except subprocess.CalledProcessError:
        return 1


config = {}
if __name__ == "__main__":
    global config
    if os.path.exists("ci/c2c.yaml"):
        config = yaml.load("ci/c2c.yaml", Loader=yaml.SafeLoader)
    code = 0
    code = max(code, check_black_config())
    code = max(check_editorconfig())
    code = max(check_gitattribute())
    code = max(check_eof())
    code = max(check_workflows())
    code = max(check_required_workflows())
    sys.exit(code)
