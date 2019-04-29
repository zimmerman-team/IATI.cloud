# encoding: utf-8
# Created by Jeremy Bowman on Mon Feb  1 12:48:09 EST 2016
# Copyright (c) 2016 Safari Books Online. All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE file for details.
"""
Utility functions for Yet Another Django Profiler
"""

import marshal
import os
import subprocess
import sys
import tempfile


def run_gprof2dot(profiler):
    """Run gprof2dot.py on the data from the provided profiler to generate a
    call graph in PDF format.

    :param profiler The profiler containing the data to be graphed
    :return A tuple of the subprocess return code and its stdout (the PDF data)
    """
    with tempfile.NamedTemporaryFile() as stats:
        stats.write(marshal.dumps(profiler.stats))
        stats.flush()
        cmd = ('gprof2dot.py -f pstats {} | dot -Tpdf'.format(stats.name))
        env = os.environ.copy()
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, env=env)
        output = process.communicate()[0]
        return_code = process.poll()
    return return_code, output
