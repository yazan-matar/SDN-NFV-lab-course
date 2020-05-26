import logging
import sys
from textwrap import dedent

from IPython import start_ipython

import sys


def run():
    """Run the PoliCONF/IPython shell."""

    # TODO: migliorare logger (leggere meglio documentazione)
    #   Ricordarsi che ora il logger è impostato in modalità scrittura (non append)

    logging.basicConfig()
    # logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s: \n%(message)s\n', filename='log.txt', filemode='w', level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger('policonf').setLevel(logging.INFO)

    start_ipython(argv=[sys.argv[0], "-i", "-c", dedent("""
    %load_ext policonf
    %polifun
    """).strip()])


if __name__ == '__main__':
    run()
