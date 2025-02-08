import dataclasses
from abc import abstractmethod
from enum import IntEnum

from bookprices.shared.config.config import Config


class JobExitStatus(IntEnum):
    SUCCESS = 0
    FAILURE = 1


@dataclasses.dataclass(frozen=True)
class JobResult:
    exit_status: JobExitStatus
    error_message: Exception | None = None


class JobBase:

    def __init__(self, config: Config) -> None:
        self.config = config

    @abstractmethod
    def start(self, **kwargs) -> JobResult:
        pass
