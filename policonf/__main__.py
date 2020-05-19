import logging
import sys
from textwrap import dedent

from IPython import start_ipython


def run():
    """Run the PoliCONF/IPython shell."""

    # TODO: migliorare logger (leggere meglio documentazione)
    #   Ricordarsi che ora il logger è impostato in modalità scrittura (non append)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s: \n%(message)s\n', filename='log.txt', filemode='w', level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger('policonf').setLevel(logging.INFO)

    # handler = logging.StreamHandler(sys.stdout)
    # handler.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # logging.getLogger().addHandler(handler)

    start_ipython(argv=[sys.argv[0], "-i", "-c", dedent("""
    %load_ext policonf
    %polifun
    """).strip()])


if __name__ == '__main__':
    run()
