import logging
import sys
from textwrap import dedent

from IPython import start_ipython


def run():
    """Run the PoliCONF/IPython shell."""
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger('policonf').setLevel(logging.DEBUG)

    start_ipython(argv=[sys.argv[0], "-i", "-c", dedent("""
    %load_ext policonf
    %polifun
    """).strip()])


if __name__ == '__main__':
    run()
