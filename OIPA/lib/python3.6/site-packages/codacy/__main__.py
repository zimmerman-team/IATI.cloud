#!/usr/bin/env python
from __future__ import absolute_import

import sys
from . import __name__
from .reporter import run

sys.exit(run(__name__))
