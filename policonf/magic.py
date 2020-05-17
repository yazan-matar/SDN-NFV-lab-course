"""PoliCONF/IPython magic function management."""

from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers
from logging import getLogger
from textwrap import dedent

from path import Path

import policonf


#: Logger instance for mod:`policonf`.
LOG = getLogger(__package__)


class course_function:
    """Decorator for defining PoliCONF SDN course functions."""

    def __init__(self, shortcut: str):
        """Initialize with verbose `title` and execution `shortcut`."""
        self.shortcut = shortcut

    def __call__(self, func):
        """Mark `func` as PoliCONF SDN course function."""
        func._policonf_course_function = self
        return func


class polifun:
    """The ``%polifun``/``%polirun`` magic functions for IPython."""

    @staticmethod
    def course_functions():
        """
        Get available NETCONF/RESTCONF SDN course functions.

        From ``policonf/netconf-functions.py`` and
        ``policonf/restconf-functions.py``, respectively.

        On each call, the source files are reloaded from disk.

        :return:
            A ``dict`` with ``'netconf'``/``'restconf'`` keys and ``list``
            values.
        """
        LOG.info("(Re-)Loading ADVA/PoliMi SDN course functions...")

        def iterate(confmode: str):
            """Get functions for `confmode` ``'netconf'``/``'restconf'``."""
            functions_module_spec = spec_from_file_location(
                'policonf-{}-functions'.format(confmode), str(
                    Path(policonf.__file__).realpath().dirname() /
                    '{}-functions.py'.format(confmode)))

            functions_module = module_from_spec(functions_module_spec)
            functions_module_spec.loader.exec_module(functions_module)

            for name, member in getmembers(functions_module):
                if hasattr(member, '_policonf_course_function'):
                    yield member

        return {
            confmode: sorted(
                iterate(confmode),
                key=lambda func: func.__code__.co_firstlineno)
            for confmode in ('netconf', 'restconf')}

    def __call__(self, arg_line: str):
        """The actual ``%polifun`` magic."""
        functions = self.course_functions()
        for confmode in ('netconf', 'restconf'):
            print("\nAvailable ADVA/PoliMi {} SDN course functions:\n".format(
                confmode.upper()))

            for func in functions[confmode]:
                shortcut = func._policonf_course_function.shortcut
                title = func.__doc__.strip()
                print("[{}] {}".format(shortcut, title))

        print(dedent("""
        Run a course function by using the %polirun command,
        followed by either netconf(nc) or restconf(rc)
        and the function's [shortcut]

        For example, to run the RESTCONF "{}" function:

        %polirun rc {}

        For convenience, you can use %ncrun and %rcrun instead of %polirun nc
        and %polirun rc, respectively:
        
        %rcrun {}
        """.format(title, shortcut, shortcut)).rstrip())

    def run(self, arg_line: str):
        """The actual ``%polirun`` magic."""
        confmode, shortcut = arg_line.strip().split()
        confmode = confmode.lower()
        confmode = {'nc': 'netconf', 'rc': 'restconf'}.get(confmode, confmode)
        shortcut = shortcut.strip("[]")

        for func in self.course_functions()[confmode]:
            if func._policonf_course_function.shortcut == shortcut:
                return func()

        raise LookupError(
            "No {} SDN course function has shortcut [{}]".format(
                confmode.upper(), shortcut))

    def ncrun(self, arg_line: str):
        """Convenience ``%ncrun`` alternative to ``%polirun netconf``."""
        return self.run("netconf {}".format(arg_line))

    def rcrun(self, arg_line: str):
        """Convenience ``%rcrun`` alternative to ``%polirun restconf``."""
        return self.run("restconf {}".format(arg_line))


def load(shell):
    """Load magic functions from this module into the IPython `shell`."""
    polifun_magic = polifun()
    shell.magics_manager.magics['line'].update({
        'polifun': polifun_magic,
        'polirun': polifun_magic.run,

        'ncrun': polifun_magic.ncrun,
        'rcrun': polifun_magic.rcrun,
    })
