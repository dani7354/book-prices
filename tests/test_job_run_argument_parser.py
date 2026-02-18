import pytest

from bookprices.shared.service.job_service import JobRunArgumentType
from bookprices.web.service.job_run_argument_parser import JobRunArgumentParser


def test_job_run_argument_parser_parses_valid_arguments() -> None:
    argument_str = "arg1:str:value1,value2"

    result = JobRunArgumentParser.parse_argument(argument_str)

    assert result
    assert result.type == JobRunArgumentType.STRING
    assert len(result.values) == 2
    assert result.values[0] == "value1"
    assert result.values[1] == "value2"
    assert result.errors == []


def test_parse_arguments_parses_multiple_valid_args() -> None:
    argument_str = "arg1:str:value1,value2\narg2:int:1000,1001"

    result = JobRunArgumentParser.parse_arguments(argument_str)

    assert result
    assert result.success
    assert len(result.arguments) == 2
    assert result.arguments[0].type == JobRunArgumentType.STRING

    assert result.arguments[0].values[0] == "value1"
    assert result.arguments[0].values[1] == "value2"

    assert result.arguments[1].type == JobRunArgumentType.INTEGER
    assert result.arguments[1].values[0] == 1000
    assert result.arguments[1].values[1] == 1001




@pytest.mark.parametrize("arg_str", ["", None, "\n", "arg1:str"])
def test_parse_argument_invalid_str(arg_str: str) -> None:
    result = JobRunArgumentParser.parse_arguments(arg_str)

    assert not result.success