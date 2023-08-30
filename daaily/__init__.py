"""Daaily API Library for Python."""


from daaily import version as daaily_version
from daaily._auth import Credentials

__version__ = daaily_version.__version__

__all__ = ["Credentials"]
