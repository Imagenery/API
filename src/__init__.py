import tomli

with open("./pyproject.toml", "rb") as f:
    project = tomli.load(f)

__version__ = project["tool"]["poetry"]["version"]
__author__ = project["tool"]["poetry"]["authors"][0]

from .app import app
