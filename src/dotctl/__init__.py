from importlib.metadata import version as pkg_version, PackageNotFoundError
import os

__APP_NAME__ = "dotctl"
try:
    __APP_VERSION__ = pkg_version("dotctl")
except PackageNotFoundError:
    __APP_VERSION__ = "0.0.0"
__BASE_DIR__ = os.path.dirname(os.path.abspath(__file__))
__DEFAULT_PROFILE__ = "default"
