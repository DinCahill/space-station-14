#!/usr/bin/env python3
# Installs git hooks, updates them, updates submodules, that kind of thing.

import subprocess
import sys
import os
import shutil
from pathlib import Path
from typing import List

SOLUTION_PATH = Path("..") / "SpaceStation14.sln"
# If this doesn't match the saved version we overwrite them all.
CURRENT_HOOKS_VERSION = "2"
QUIET = len(sys.argv) == 2 and sys.argv[1] == "--quiet"


def run_command(command: List[str], capture: bool = False) -> subprocess.CompletedProcess:
    """
    Runs a command with pretty output.
    """
    text = ' '.join(command)
    if not QUIET:
        print("$ {}".format(text))

    sys.stdout.flush()

    completed = None

    if capture:
        completed = subprocess.run(command, cwd="..", stdout=subprocess.PIPE)
    else:
        completed = subprocess.run(command, cwd="..")

    if completed.returncode != 0:
        print("Error: command exited with code {}!".format(completed.returncode))

    return completed


def update_submodules():
    """
    Updates all submodules.
    """

    if Path("DISABLE_SUBMODULE_AUTOUPDATE").is_file():
        return

    # If the status doesn't match, force VS to reload the solution.
    # status = run_command(["git", "submodule", "status"], capture=True)
    run_command(["git", "submodule", "update", "--init", "--recursive"])
    # status2 = run_command(["git", "submodule", "status"], capture=True)

    # Something changed.
    # if status.stdout != status2.stdout:
    #     print("Git submodules changed. Reloading solution.")
    #     reset_solution()


def install_hooks():
    """
    Installs the necessary git hooks into .git/hooks.
    """

    # Read version file.
    if Path("INSTALLED_HOOKS_VERSION").is_file():
        with Path("INSTALLED_HOOKS_VERSION").open("r") as f:
            if f.read() == CURRENT_HOOKS_VERSION:
                if not QUIET:
                    print("No hooks change detected.")
                #return

    with Path("INSTALLED_HOOKS_VERSION").open("w") as f:
        f.write(CURRENT_HOOKS_VERSION)

    print("Hooks need updating.")

    hooks_target_dir = Path("..")/".git"/"hooks"
    hooks_source_dir = Path("hooks")

    # Clear entire tree since we need to kill deleted files too.
    for file in hooks_target_dir.iterdir():
        file.unlink()

    for file in hooks_source_dir.iterdir():
        print("Copying hook {}".format(file.name))
        shutil.copy2(file, hooks_target_dir/file.name)


def reset_solution():
    """
    Force VS to think the solution has been changed to prompt the user to reload it, thus fixing any load errors.
    """

    with SOLUTION_PATH.open("r") as f:
        content = f.read()

    with SOLUTION_PATH.open("w") as f:
        f.write(content)


if __name__ == '__main__':
    install_hooks()
    update_submodules()
