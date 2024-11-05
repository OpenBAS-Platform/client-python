# -*- coding: utf-8 -*-
__version__ = "1.8.1"

from pyobas._version import (  # noqa: F401
    __author__,
    __copyright__,
    __email__,
    __license__,
    __title__,
)
from pyobas.client import OpenBAS  # noqa: F401
from pyobas.contracts import *  # noqa: F401,F403,F405
from pyobas.exceptions import *  # noqa: F401,F403,F405

__all__ = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__title__",
    "__version__",
    "OpenBAS",
]
__all__.extend(exceptions.__all__)  # noqa: F405
