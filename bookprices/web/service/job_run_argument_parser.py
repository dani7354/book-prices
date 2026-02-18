import os
import string
from dataclasses import dataclass, field
from typing import ClassVar

from sqlalchemy.sql.coercions import cls

from bookprices.shared.service.job_service import JobRunArgumentType


@dataclass(frozen=False)
class ParsedJobRunArgumentResult:
    name: str = ""
    type: JobRunArgumentType | None = None
    values: list[str] | list[int] | list[bool] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class JobRunArgumentsParsingResult:
    arguments: list[ParsedJobRunArgumentResult]

    @property
    def success(self) -> bool:
        return self.arguments and not any(parsed_argument.errors for parsed_argument in self.arguments)

    @property
    def errors_messages(self) -> list[str]:
        return [error for parsed_argument in self.arguments for error in parsed_argument.errors]


class JobRunArgumentParser:
    """ Parser for job run arguments in POST request (form). Format: <name>:<type>:<value1>,<value2>,... """
    _argument_str_tuple_size: ClassVar[int] = 3
    _arguments_delimiter: ClassVar[str] = os.linesep
    _name_values_delimiter: ClassVar[str] = ":"
    _values_delimiter: ClassVar[str] = ","
    _values_valid_chars: ClassVar[str] = string.ascii_letters + string.digits


    @classmethod
    def parse_arguments(cls, arguments_str: str) -> JobRunArgumentsParsingResult:
        if not arguments_str:
            return JobRunArgumentsParsingResult(arguments=[])

        argument_strs = arguments_str.split(cls._arguments_delimiter)
        parsed_arguments = [argument for a in argument_strs if (argument := cls.parse_argument(a))]

        return JobRunArgumentsParsingResult(arguments=parsed_arguments)

    @classmethod
    def parse_argument(cls, argument_str: str) -> ParsedJobRunArgumentResult:
        parsed_job_run_argument_result = ParsedJobRunArgumentResult()
        try:
            name, value_type, values_str = argument_str.split(cls._name_values_delimiter, cls._argument_str_tuple_size)
            if cls._is_name_valid(name):
                parsed_job_run_argument_result.name = name
            else:
                parsed_job_run_argument_result.errors.append(f"Invalid argument name: {name}")

            if argument_type := cls._parse_type(value_type):
                parsed_job_run_argument_result.type = argument_type
            else:
                parsed_job_run_argument_result.errors.append(f"Invalid argument type: {value_type}")

            if (values := values_str.split(cls._values_delimiter)) and all(cls._are_chars_valid(value) for value in values):
                parsed_job_run_argument_result.values = cls._parse_values(values, argument_type)
            else:
                parsed_job_run_argument_result.errors.append(f"Invalid characters or missing values for argument {name}")
        except ValueError as e:
            parsed_job_run_argument_result.errors.append(f"Invalid argument format. Error: {e}")

        return parsed_job_run_argument_result

    @classmethod
    def _is_name_valid(cls, name: str) -> bool:
        return len(name) > 0 and cls._are_chars_valid(name)

    @classmethod
    def _parse_type(cls, type_str: str) -> JobRunArgumentType | None:
        try:
            return JobRunArgumentType(type_str)
        except ValueError:
            return None

    @classmethod
    def _parse_values(cls, values: list[str], value_type: JobRunArgumentType) -> list[str | int | bool]:
        parsed_values = []
        for value in values:
            if not cls._are_chars_valid(value):
                continue
            if (parsed_value := cls._parse_value(value, value_type)) is not None:
                parsed_values.append(parsed_value)

        return parsed_values

    @classmethod
    def _parse_value(cls, value_str, argument_type: JobRunArgumentType) -> str | int | bool | None:
        if argument_type == JobRunArgumentType.INTEGER:
            return cls._parse_value_int(value_str)
        elif argument_type == JobRunArgumentType.BOOLEAN:
            return cls._parse_value_bool(value_str)
        else:
            return value_str

    @classmethod
    def _are_chars_valid(cls, value_str: str) -> bool:
        return all(char in cls._values_valid_chars for char in value_str)

    @staticmethod
    def _parse_value_int(value_str: str) -> int | None:
        try:
            return int(value_str.strip())
        except ValueError:
            return None

    @staticmethod
    def _parse_value_bool(value_str: str) -> bool | None:
        if value_str.lower() in {"true", "1"}:
            return True
        elif value_str.lower() in {"false", "0"}:
            return False
        else:
            return None