# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 11:16:36 EST 2014
# Copyright (c) 2014, 2015 Safari Books Online. All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE file for details.
"""
Yet Another Django Profiler middleware implementation
"""

from __future__ import unicode_literals

import cProfile
import logging
import os
import pstats

try:
    from unittest import mock
except ImportError:
    import mock

from django.core.exceptions import MiddlewareNotUsed
from django.utils.six.moves import cStringIO as StringIO
from django.utils.translation import ugettext as _

from .conf import settings
from .utils import run_gprof2dot

log = logging.getLogger(__name__)


def func_strip_path(func_name):
    """Replacement for pstats.func_strip_path which yields qualified module names"""
    filename, line, name = func_name
    return settings.path_to_module_function(filename), line, name


def in_request(request, parameter):
    """Determine if the request contains the specified parameter, whether it's
    a GET or a POST."""
    return parameter in request.GET or parameter in request.POST


def set_content(response, content):
    """Set the content of the provided response, whether or not it's streaming"""
    if response.streaming:
        # No point in consuming the previous iterator, the profiler has
        # already stopped
        response.streaming_content = [content]
    else:
        response.content = content


def text_response(response, content):
    """Return a plain text message as the response content."""
    set_content(response, content)
    response['Content-type'] = 'text/plain'
    return response


def which(program):
    """Return the path of the named program in the PATH, or None if no such
    executable program can be found  Used to make sure that required binaries
    are in place before attempting to call them."""

    def is_exe(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    program_path, _name = os.path.split(program)
    if program_path:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class ProfilerMiddleware(object):
    """
    Code profiling middleware which can display either a call graph PDF or
    a table of called functions ordered by the desired statistic.  For the call
    graph, just append "?profile" to the URL.  For the graph generation to
    work, install Graphviz from http://www.graphviz.org/Download.php

    For a statistics table, use the statistic you want to sort by as the
    parameter (such as "?profile=time").  Sorting options include:

    * calls (call count)
    * cumulative (cumulative time)
    * file (file name)
    * module (file name)
    * pcalls (primitive call count)
    * line (line number)
    * name (function name)
    * nfl (name/file/line)
    * stdname (standard name)
    * time (internal time)

    Additional parameters can be added when generating a statistics table:

    * fraction - The fraction of total function calls to display (the default of .2 is omitted if max_calls or pattern are specified)
    * max_calls - The maximum number of function calls to display
    * pattern - Regular expression filter for function display names

    To get these instructions in the app if you forget the usage options, use
    "?profile=help" in the URL.

    Inspiration:

    * https://gist.github.com/kesor/1229681
    * https://bitbucket.org/brodie/geordi
    """

    def __init__(self, get_response=None):
        if not settings.YADP_ENABLED:
            # Disable the middleware completely when YADP_ENABLED = False
            raise MiddlewareNotUsed()
        self.get_response = get_response
        self.error = None
        self.profiler = None
        self.get_parameters = None
        self.post_parameters = None
        self.clock_parameter = None
        self.fraction_parameter = None
        self.max_calls_parameter = None
        self.pattern_parameter = None
        self.profile_parameter = None

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def get_parameter(self, name):
        """Get the specified parameter from the request, whether it's a GET or a
        POST, and then removes it so it doesn't interfere with the view's
        normal operation.  Returns `None` if it is not present.
        Search in GET (and stop if found), then in POST."""
        if self.get_parameters is not None and name in self.get_parameters:
            value = self.get_parameters.get(name, None)
            self.get_parameters.pop(name)
            return value

        if self.post_parameters is not None and name in self.post_parameters:
            value = self.post_parameters.get(name, None)
            self.post_parameters.pop(name)
            return value

        return None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        self.profile_parameter = None
        if settings.YADP_ENABLED and in_request(request, settings.YADP_PROFILE_PARAMETER):
            self.error = None
            self.get_parameters = request.GET.copy()
            request.GET = self.get_parameters
            self.post_parameters = request.POST.copy()
            request.POST = self.post_parameters
            self.fraction_parameter = self.get_parameter(settings.YADP_FRACTION_PARAMETER)
            self.max_calls_parameter = self.get_parameter(settings.YADP_MAX_CALLS_PARAMETER)
            self.pattern_parameter = self.get_parameter(settings.YADP_PATTERN_PARAMETER)
            self.profile_parameter = self.get_parameter(settings.YADP_PROFILE_PARAMETER)
            if settings.YADP_PROFILER_BACKEND == 'yappi':
                try:
                    from .yadp_yappi import YappiProfile
                    wall = self.get_parameter(settings.YADP_CLOCK_PARAMETER) == 'wall'
                    self.profiler = YappiProfile(wall=wall)
                except Exception as e:
                    log.exception(e)
                    self.error = _('Could not find Yappi; please install Yappi to be able to use it for profiling')
                    return None
            else:
                self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if self.profile_parameter is not None:
            if self.error:
                return text_response(response, self.error)
            self.profiler.create_stats()
            mode = self.profile_parameter
            if mode == 'file':
                # Work around bug on Python versions >= 2.7.4
                mode = 'fil'
            if not mode:
                if not which('dot'):
                    return text_response(response, _('Could not find "dot" from Graphviz; please install Graphviz to enable call graph generation'))
                if not which('gprof2dot.py'):
                    return text_response(response, _('Could not find gprof2dot.py, which should have been installed by yet-another-django-profiler'))
                return_code, output = run_gprof2dot(self.profiler)
                if return_code:
                    raise Exception(_('gprof2dot.py exited with {return_code}').format(return_code=return_code))
                set_content(response, output)
                response['Content-Type'] = 'application/pdf'
                return response
            elif mode == 'help':
                return text_response(response, ProfilerMiddleware.__doc__)
            else:
                out = StringIO()
                stats = pstats.Stats(self.profiler, stream=out)

                with mock.patch('pstats.func_strip_path') as mock_func_strip_path:
                    mock_func_strip_path.side_effect = func_strip_path
                    stats.strip_dirs()
                restrictions = []
                if self.pattern_parameter is not None:
                    restrictions.append(self.pattern_parameter)
                if self.fraction_parameter is not None:
                    restrictions.append(float(self.fraction_parameter))
                elif self.max_calls_parameter is not None:
                    restrictions.append(int(self.max_calls_parameter))
                elif self.pattern_parameter is None:
                    restrictions.append(.2)
                stats.sort_stats(mode).print_stats(*restrictions)
                return text_response(response, out.getvalue())
        return response
