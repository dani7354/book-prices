import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

from bookprices.shared.service.job_service import JobRunArgumentSchemaFields


class JobRunArgumentName(StrEnum):
    BOOK_IDS = "bookids"


@dataclass(frozen=True)
class JobRunArgumentTypeInfo:
    name: JobRunArgumentName
    argument_type: type
    is_list: bool


class JobRunArgumentService:
    """ Service for reading and validating job run arguments. """

    _invalid_argument_type_error_msg: ClassVar[str] = "Invalid argument type for {name}"

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._argument_name_to_type_map: dict[JobRunArgumentName, JobRunArgumentTypeInfo] = {
            JobRunArgumentName.BOOK_IDS: JobRunArgumentTypeInfo(
                name=JobRunArgumentName.BOOK_IDS, argument_type=int, is_list=True)
        }

    def parse_argument(self, name: JobRunArgumentName, **kwargs):
        if not (argument_value := kwargs.get(name)):
            self._logger.error(f"Argument {name} not in dictionary.")
            return None

        type_info = self._argument_name_to_type_map[name]
        if type_info.is_list:
            if not isinstance(argument_value, list):
                self._logger.error(f"Argument {name} is not a list.")
                return None

            if not all(isinstance(v, type_info.argument_type) for v in argument_value):
                self._logger.error(self._invalid_argument_type_error_msg.format(name=name))
                return None
        else:
            if not isinstance(argument_value, type_info.argument_type):
                self._logger.error(self._invalid_argument_type_error_msg.format(name=name))
                return None

        return argument_value

    def create_job_run_payload(self, argument_names: list[JobRunArgumentName], **kwargs) -> list:
        arguments_payload = []
        for name in argument_names:
            if not (arg_values := self.parse_argument(name, **kwargs)):
                continue

            arg_values_str_arr = [str(v) for v in arg_values] if isinstance(arg_values, list) else [str(arg_values)]
            arguments_payload.append({
                JobRunArgumentSchemaFields.NAME: name,
                JobRunArgumentSchemaFields.TYPE: str(self._argument_name_to_type_map[name].argument_type.__name__),
                JobRunArgumentSchemaFields.VALUES: arg_values_str_arr
            })

        return arguments_payload


