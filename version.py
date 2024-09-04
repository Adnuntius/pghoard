# Copied from https://github.com/ohmu/ohmu_common_py version.py version 0.0.1-0-unknown-fa54b44
"""
pghoard - version detection and version.py __version__ generation

Copyright (c) 2015 Ohmu Ltd
See LICENSE for details
"""

import importlib
import os
import subprocess


def load_source(modname, filename):
    loader = importlib.machinery.SourceFileLoader(modname, filename)
    spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
    module = importlib.util.module_from_spec(spec)
    # The module is always executed and not cached in sys.modules.
    # Uncomment the following line to cache the module.
    # sys.modules[module.__name__] = module
    loader.exec_module(module)
    return module


def save_version(new_ver, old_ver, version_file):
    if not new_ver:
        return False
    version_file = os.path.join(os.path.dirname(__file__), version_file)
    if not old_ver or new_ver != old_ver:
        with open(version_file, "w") as fp:
            fp.write("__version__ = '{}'\n".format(new_ver))
    return True


def get_project_version(version_file):
    version_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), version_file)
    try:
        module = load_source("verfile", version_file)
        file_ver = module.__version__
    except IOError:
        file_ver = None

    os.chdir(os.path.dirname(__file__) or ".")
    try:
        git_out = subprocess.check_output(["git", "describe", "--always"],
                                          stderr=getattr(subprocess, "DEVNULL", None))
    except (OSError, subprocess.CalledProcessError):
        pass
    else:
        git_ver = git_out.splitlines()[0].strip().decode("utf-8")
        if "." not in git_ver:
            git_ver = "0.0.1-0-unknown-{}".format(git_ver)
        if save_version(git_ver, file_ver, version_file):
            return git_ver

    makefile = os.path.join(os.path.dirname(__file__), "Makefile")
    if os.path.exists(makefile):
        with open(makefile, "r") as fp:
            lines = fp.readlines()
        short_ver = [line.split("=", 1)[1].strip() for line in lines if line.startswith("short_ver")][0]
        if save_version(short_ver, file_ver, version_file):
            return short_ver

    if not file_ver:
        raise Exception("version not available from git or from file {!r}".format(version_file))

    return file_ver

if __name__ == "__main__":
    import sys
    get_project_version(sys.argv[1])
