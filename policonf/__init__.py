from logging import getLogger

import policonf.magic


#: Logger instance for mod:`policonf`.
LOG = getLogger(__package__)


def load_ipython_extension(shell):
    """
    Automagically Called by IPython on ``%load_ext policonf``.

    Adds all the PoliCONF magic functions to the IPython `shell`
    """
    LOG.info("Loading PoliCONF/IPython magic...")

    policonf.magic.load(shell=shell)
