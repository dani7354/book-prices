import os
import logging
from argparse import ArgumentParser, Namespace

THREAD_COUNT = 10


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def setup_logging(directory: str, filename_base: str, loglevel: int):
    logfile = os.path.join(directory, filename_base)
    logging.basicConfig(
        filename=logfile,
        filemode="a",
        format='%(asctime)s - %(levelname)s: %(message)s',
        level=loglevel)
    logging.getLogger().addHandler(logging.StreamHandler())
