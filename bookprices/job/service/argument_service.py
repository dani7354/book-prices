import logging
from enum import StrEnum
from typing import Any

from bookprices.job.runner.service import JobRunArgument


class JobRunArgumentName(StrEnum):
    BOOK_IDS = "bookids"


class JobRunArgumentService:

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._argument_name_to_type_map: dict[JobRunArgumentName, type] = {
            JobRunArgumentName.BOOK_IDS: list[int]
        }

    def parse_argument(self, kwargs: dict[str, Any], name: JobRunArgumentName):
        if name not in kwargs:
            self._logger.error("Argument %s not in dictionary.", name)
            return None

        if not kwargs[name] or not isinstance(kwargs[name], self._argument_name_to_type_map[name]):
            self._logger.error(f"Invalid argument type for {name}")
            return None

        return kwargs[name]