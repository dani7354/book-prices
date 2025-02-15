import logging
import os
from datetime import date

from bookprices.shared.config.config import Config


def setup_logging(config: Config) -> None:
    loglevel = logging.getLevelNamesMapping()[config.loglevel]
    directory = config.logdir
    filename_base = f"JobRunner_{date.today().month:02d}-{date.today().year}.log"
    logfile = os.path.join(directory, filename_base)
    logging.basicConfig(
        filename=logfile,
        filemode="a",
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=loglevel)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info(f"Logging to {logfile} at level {loglevel}")
