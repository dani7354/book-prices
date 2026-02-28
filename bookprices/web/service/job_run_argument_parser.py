import os
import string
from dataclasses import dataclass, field
from typing import ClassVar

from bookprices.shared.service.job_service import JobRunArgumentType, JobRunArgumentSchemaFields


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

    def get_result_dict(self) -> list[dict[str, str | list[str | int | bool]]]:
        return [
            {
                JobRunArgumentSchemaFields.NAME: argument.name,
                JobRunArgumentSchemaFields.TYPE: str(argument.type.value) if argument.type else None,
                JobRunArgumentSchemaFields.VALUES: [str(v) for v in argument.values]
            }
            for argument in self.arguments
        ]


class JobRunArgumentParser:
    """ Parser for job run arguments in POST request (form). Format: <name>:<type>:<value1>,<value2>,... """
    _argument_str_tuple_size: ClassVar[int] = 3
    _arguments_delimiter: ClassVar[str] = os.linesep
    _name_values_delimiter: ClassVar[str] = ":"
    _values_delimiter: ClassVar[str] = ","
    _invalid_char_replacement: ClassVar[str] = "_"
    _values_valid_chars: ClassVar[set[str]] = set(string.ascii_letters + string.digits)

    def __init__(self) -> None:
        pass

    def parse_arguments(self, arguments_str: str) -> JobRunArgumentsParsingResult:
        if not arguments_str:
            return JobRunArgumentsParsingResult(arguments=[])

        argument_strs = arguments_str.split(self._arguments_delimiter)
        parsed_arguments = [self._parse_argument(a) for a in argument_strs]

        return JobRunArgumentsParsingResult(arguments=parsed_arguments)

    def create_arguments_str(self, arguments: list[tuple[str, str, list[str | int | bool]]]) -> str:
        argument_strs = []
        for name, value_type, values in arguments:
            values_str = self._values_delimiter.join(str(v) for v in values)
            argument_strs.append(f"{name}{self._name_values_delimiter}{value_type}{self._name_values_delimiter}{values_str}")

        return self._arguments_delimiter.join(argument_strs)

    def _parse_argument(self, argument_str: str) -> ParsedJobRunArgumentResult:
        parsed_job_run_argument_result = ParsedJobRunArgumentResult()
        try:
            name, value_type, values_str = argument_str.split(self._name_values_delimiter, self._argument_str_tuple_size)
            if self._is_name_valid(name):
                parsed_job_run_argument_result.name = name
            else:
                parsed_job_run_argument_result.errors.append(
                    f"Invalid argument name: {self._sanitise_for_output(name)}")

            if argument_type := self._parse_type(value_type):
                parsed_job_run_argument_result.type = argument_type
            else:
                parsed_job_run_argument_result.errors.append(
                    f"Invalid argument type: {self._sanitise_for_output(value_type)}")

            if values := values_str.split(self._values_delimiter):
                success, parsed_values = self._parse_values(values, argument_type)
                parsed_job_run_argument_result.values = parsed_values
                parsed_job_run_argument_result.errors.append("Failed to parse one or more values!") if not success else None
            else:
                parsed_job_run_argument_result.errors.append(
                    f"Invalid characters or missing values for argument {self._sanitise_for_output(name)}")
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

    def _parse_values(
            self,
            values: list[str],
            value_type: JobRunArgumentType) -> tuple[bool, list[str | int | bool]]:
        errors, parsed_values = [], []
        success = any(values)
        for value in values:
            if not self._are_chars_valid(value):
                success = False
            if (parsed_value := self._parse_value(value, value_type)) is not None:
                parsed_values.append(parsed_value)
            else:
                success = False

        return success, parsed_values

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

    @classmethod
    def _sanitise_for_output(cls, value: str) -> str:
        return "".join([c if c in cls._values_valid_chars else cls._invalid_char_replacement for c in value])

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