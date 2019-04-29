# encoding: utf-8
# Created by Jeremy Bowman on Fri Feb 21 11:16:36 EST 2014
# Copyright (c) 2014, 2015 Safari Books Online. All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE file for details.
"""
Yet Another Django Profiler "profile" management command
"""

from __future__ import unicode_literals

import argparse
import atexit
import cProfile
from optparse import make_option
import pstats
import sys

try:
    from unittest import mock
except ImportError:
    import mock

import django
from django.conf import settings as django_settings
from django.core.management import call_command, ManagementUtility
from django.core.management.base import BaseCommand
from django.utils.six.moves import cStringIO as StringIO

from yet_another_django_profiler.conf import settings
from yet_another_django_profiler.middleware import func_strip_path, which
from yet_another_django_profiler.utils import run_gprof2dot

OPTIONS = (
    (('-o', '--output'), {'dest': 'path', 'help': 'Path to a file in which to store the profiling output (required if generating a call graph PDF, other results are output to the console by default)'}),
    (('-s', '--sort'), {'dest': 'sort', 'help': 'Statistic by which to sort the profiling data (default is to generate a call graph PDF instead)'}),
    (('-f', '--fraction'), {'dest': 'fraction', 'help': 'The fraction of total function calls to display (the default of .2 is omitted if max-calls or pattern are specified)'}),
    (('-m', '--max-calls'), {'dest': 'max_calls', 'help': 'The maximum number of function calls to display'}),
    (('-p', '--pattern'), {'dest': 'pattern', 'help': 'Regular expression filter for function display names'}),
    (('-b', '--backend'), {'dest': 'backend', 'default': 'cProfile', 'help': 'Profiler backend to use (cProfile or yappi)'}),
    (('-c', '--clock'), {'dest': 'clock', 'default': 'cpu', 'help': 'Yappi clock type to use (cpu or wall)'}),
)


class Command(BaseCommand):
    """
    Django management command for profiling other management commands.
    """
    args = 'other_command <argument argument ...>'
    help = 'Profile another Django management command'
    # Command line arguments for Django 1.7 and below
    custom_options = tuple([make_option(*option[0], **option[1]) for option in OPTIONS])

    @property
    def use_argparse(self):
        return not (django.VERSION[0] == 1 and django.VERSION[1] < 8)

    def add_arguments(self, parser):
        """Command line arguments for Django 1.8+"""
        for option in OPTIONS:
            parser.add_argument(*option[0], **option[1])
        parser.add_argument('other_command', help='The management command to be profiled')
        parser.add_argument(
            'command_arguments', nargs=argparse.REMAINDER, help='Arguments of the management command being profiled')

    def create_parser(self, prog_name, subcommand):
        """
        Override the base create_parser() method to ignore options of the
        command being profiled.
        """
        if not self.use_argparse:
            self.__class__.option_list = BaseCommand.option_list + self.custom_options
        parser = super(Command, self).create_parser(prog_name, subcommand)
        if not self.use_argparse:
            parser.disable_interspersed_args()
        return parser

    def handle(self, *args, **options):
        """
        Run and profile the specified management command with the provided
        arguments.
        """
        if not self.use_argparse and not len(args):
            self.print_help(sys.argv[0], 'profile')
            sys.exit(1)
        if not options['sort'] and not options['path']:
            self.stdout.write('Output file path is required for call graph generation')
            sys.exit(1)

        if self.use_argparse:
            command_name = options['other_command']
        else:
            command_name = args[0]
        utility = ManagementUtility(sys.argv)
        command = utility.fetch_command(command_name)
        parser = command.create_parser(sys.argv[0], command_name)
        if self.use_argparse:
            command_options = parser.parse_args(options['command_arguments'])
            command_args = vars(command_options).pop('args', ())
        else:
            command_options, command_args = parser.parse_args(list(args[1:]))

        if command_name == 'test' and django_settings.TEST_RUNNER == 'django_nose.NoseTestSuiteRunner':
            # Ugly hack: make it so django-nose won't have nosetests choke on
            # our parameters
            BaseCommand.option_list += self.custom_options

        if options['backend'] == 'yappi' or (settings.YADP_PROFILER_BACKEND == 'yappi' and not options['backend']):
            import yet_another_django_profiler.yadp_yappi as yadp_yappi
            profiler = yadp_yappi.YappiProfile(wall=options['clock'] == 'wall')
        else:
            profiler = cProfile.Profile()

        if 'testing' not in options:
            atexit.register(output_results, profiler, options, self.stdout)
        profiler.runcall(call_command, command_name, *command_args, stderr=self.stderr,
                         stdout=self.stdout, **vars(command_options))
        if 'testing' in options:
            output_results(profiler, options, self.stdout)
        else:
            sys.exit(0)


def output_results(profiler, options, stdout):
    """Generate the profiler output in the desired format.  Implemented as a
    separate function so it can be run as an exit handler (because management
    commands often call exit() directly, bypassing the rest of the profile
    command's handle() method)."""
    profiler.create_stats()

    if not options['sort']:
        if not which('dot'):
            stdout.write('Could not find "dot" from Graphviz; please install Graphviz to enable call graph generation')
            return
        if not which('gprof2dot.py'):
            stdout.write('Could not find gprof2dot.py, which should have been installed by yet-another-django-profiler')
            return
        return_code, output = run_gprof2dot(profiler)
        if return_code:
            stdout.write('gprof2dot/dot exited with {}'.format(return_code))
            return
        path = options['path']
        with open(path, 'wb') as pdf_file:
            pdf_file.write(output)
            stdout.write('Wrote call graph to {}'.format(path))
    else:
        sort = options['sort']
        if sort == 'file':
            # Work around bug on Python versions >= 2.7.4
            sort = 'fil'
        out = StringIO()
        stats = pstats.Stats(profiler, stream=out)
        with mock.patch('pstats.func_strip_path') as mock_func_strip_path:
            mock_func_strip_path.side_effect = func_strip_path
            stats.strip_dirs()
        restrictions = []
        if options['pattern']:
            restrictions.append(options['pattern'])
        if options['fraction']:
            restrictions.append(float(options['fraction']))
        elif options['max_calls']:
            restrictions.append(int(options['max_calls']))
        elif not options['pattern']:
            restrictions.append(.2)
        stats.sort_stats(sort).print_stats(*restrictions)
        if options['path']:
            path = options['path']
            with open(path, 'w') as text_file:
                text_file.write(out.getvalue())
                stdout.write('Wrote profiling statistics to {}'.format(path))
        else:
            stdout.write(out.getvalue())
