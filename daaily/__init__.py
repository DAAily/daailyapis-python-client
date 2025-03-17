"""Daaily API Library for Python."""


import logging

from daaily import version as daaily_version
from daaily.credentials import Credentials

__version__ = daaily_version.__version__

__all__ = ["Credentials"]

logging.getLogger(__name__).addHandler(logging.NullHandler())
