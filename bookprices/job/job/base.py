import dataclasses
from abc import abstractmethod, ABC
from enum import IntEnum

from bookprices.shared.config.config import Config


DEFAULT_THREAD_COUNT = 8


class JobExitStatus(IntEnum):
    SUCCESS = 0
    FAILURE = 1


@dataclasses.dataclass(frozen=True)
class JobResult:
    exit_status: JobExitStatus
    error_message: Exception | None = None


class JobBase(ABC):

    def __init__(self, config: Config) -> None:
        self.config = config
        self._thread_count = config.job_thread_count or DEFAULT_THREAD_COUNT

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def start(self, **kwargs) -> JobResult:
        pass
