#!/usr/bin/env python3
import argparse
import logging
import sys
from datetime import datetime, timezone
from queue import Queue
from threading import Thread
from configuration.config import ConfigLoader



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def run():
    args = parse_arguments()
    configuration = ConfigLoader.load(args.configuration)
    setup_logging(configuration.logfile, configuration.loglevel)


if __name__ == "__main__":
    run()