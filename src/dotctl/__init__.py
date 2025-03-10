from importlib.metadata import version as pkg_version, PackageNotFoundError

__APP_NAME__ = "dotctl"
try:
    __APP_VERSION__ = pkg_version("dotctl")
except PackageNotFoundError:
    __APP_VERSION__ = "0.0.0"
