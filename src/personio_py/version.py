from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("personio-py")
except PackageNotFoundError:  # package is not installed (e.g. running from the source tree)
    __version__ = "0.0.0"
