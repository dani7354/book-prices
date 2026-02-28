import pytest

from bookprices.shared.service.job_service import JobRunArgumentType
from bookprices.web.service.job_run_argument_parser import JobRunArgumentParser


@pytest.fixture
def argument_parser() -> JobRunArgumentParser:
    return JobRunArgumentParser()


def test_job_run_argument_parser_parses_valid_arguments(argument_parser: JobRunArgumentParser) -> None:
    argument_str = "arg1:str:value1,value2"

    result = argument_parser._parse_argument(argument_str)

    assert result
    assert result.type == JobRunArgumentType.STRING
    assert len(result.values) == 2
    assert result.values[0] == "value1"
    assert result.values[1] == "value2"
    assert result.errors == []


def test_parse_arguments_parses_multiple_valid_args(argument_parser: JobRunArgumentParser) -> None:
    argument_str = "arg1:str:value1,value2\narg2:int:1000,1001"

    result = argument_parser.parse_arguments(argument_str)

    assert result
    assert result.success
    assert len(result.arguments) == 2
    assert result.arguments[0].type == JobRunArgumentType.STRING

    assert result.arguments[0].values[0] == "value1"
    assert result.arguments[0].values[1] == "value2"

    assert result.arguments[1].type == JobRunArgumentType.INTEGER
    assert result.arguments[1].values[0] == 1000
    assert result.arguments[1].values[1] == 1001


def test_parse_arguments_parses_multiple_with_one_invalid_arg(argument_parser: JobRunArgumentParser) -> None:
    argument_str = "arg1:str:value1,value2\narg2:int:1000,\narg3::1000\narg4:int:value4"

    result = argument_parser.parse_arguments(argument_str)

    assert result
    assert not result.success
    assert len(result.arguments) == 4

    assert len(result.arguments[0].errors) == 0
    assert result.arguments[0].type == JobRunArgumentType.STRING
    assert result.arguments[0].values[0] == "value1"

    assert len(result.arguments[1].errors) == 1
    assert result.arguments[1].type == JobRunArgumentType.INTEGER
    assert result.arguments[1].values[0] == 1000

    assert len(result.arguments[2].errors) == 1
    assert len(result.arguments[3].errors) == 1


@pytest.mark.parametrize("arg_str", ["", None, "\n", "arg1:str", ":::", "arg1:str:", "arg1:str:value1\n\n\n"])
def test_parse_argument_invalid_str(argument_parser: JobRunArgumentParser, arg_str: str) -> None:
    result = argument_parser.parse_arguments(arg_str)

    assert not result.success


@pytest.mark.parametrize("arg_str", [":str:value1", "<my_arg_>:int:1000", "my arg name:bool:true"])
def test_parse_arguments_fail_on_invalid_name(arg_str, argument_parser: JobRunArgumentParser) -> None:
    result = argument_parser.parse_arguments(arg_str)

    assert not result.success
    assert len(result.arguments) == 1
    assert len(result.arguments[0].errors) == 1
    assert "Invalid argument name: " in result.arguments[0].errors[0]


@pytest.mark.parametrize("arg_str", ["arg1:invalid_type:value1", "arg2::1000", "arg:bools:true"])
def test_parse_arguments_fail_on_invalid_type(arg_str, argument_parser: JobRunArgumentParser) -> None:
    result = argument_parser.parse_arguments(arg_str)

    assert not result.success
    assert len(result.arguments) == 1
    assert len(result.arguments[0].errors) == 1
    assert "Invalid argument type: " in result.arguments[0].errors[0]


@pytest.mark.parametrize("arg_str", ["arg1:str:value1, value2", "number:int:10aa00,lll", "arg:bool:falses,strue"])
def test_parse_arguments_fail_on_invalid_value(arg_str, argument_parser: JobRunArgumentParser) -> None:

    result = argument_parser.parse_arguments(arg_str)

    assert not result.success
    assert len(result.arguments) == 1
    assert len(result.arguments[0].errors) == 1
    assert "Failed to parse one or more values!" in result.arguments[0].errors[0]