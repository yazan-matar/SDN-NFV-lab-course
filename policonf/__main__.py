import logging
import sys
from textwrap import dedent

from IPython import start_ipython

import sys


def run():
    """Run the PoliCONF/IPython shell."""

    # TODO: migliorare logger (leggere meglio documentazione)
    #   Ricordarsi che ora il logger è impostato in modalità scrittura (non append)

    # logging.basicConfig()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s: \n%(message)s\n', filename='log.txt', filemode='w', level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger('policonf').setLevel(logging.INFO)
    # logging.getLogger("fileLogger").setLevel(logging.INFO)

    # handler = logging.StreamHandler(sys.stdout)
    # handler.setLevel(logging.INFO)
    # handler.setFormatter(formatter)
    # logging.getLogger().addHandler(handler)

    # Create two logger files
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: \n%(message)s\n')
    #
    # # first file logger
    # file_logger = logging.getLogger('fileLogger')
    # hdlr_1 = logging.FileHandler(filename='log.txt', mode='a')
    # hdlr_1.setFormatter(formatter)
    # file_logger.setLevel(logging.INFO)
    # file_logger.addHandler(hdlr_1)
    #
    # # second Logger
    # general_logger = logging.getLogger("policonf")
    # hdlr_2 = logging.StreamHandler(sys.stdout)
    # hdlr_2.setFormatter(formatter)
    # general_logger.setLevel(logging.INFO)
    # general_logger.addHandler(hdlr_2)

    start_ipython(argv=[sys.argv[0], "-i", "-c", dedent("""
    %load_ext policonf
    %polifun
    """).strip()])


if __name__ == '__main__':
    run()
