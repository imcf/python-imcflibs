#!/usr/bin/env python3

"""Parse project dependencies and format them for usage with `pip install`."""

# NOTE: requires Ubuntu package 'python3-tomli' to be installed!

import tomli

with open("pyproject.toml", "rb") as tomlfile:
    pyproject = tomli.load(tomlfile)

deps_pkg = pyproject["tool"]["poetry"]["dependencies"]
deps_dev = pyproject["tool"]["poetry"]["group"]["dev"]["dependencies"]

output = ""

for deps in deps_pkg, deps_dev:
    for pkg, ver in deps.items():
        if ver[0] == "^":
            ver = f">={ver[1:]}"
        output = f'{output} {pkg}{ver}'

print(output)
