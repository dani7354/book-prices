import logging
from abc import abstractmethod
from typing import Mapping, ClassVar


class Listener:
    @abstractmethod
    def notify(self, *args, **kwargs):
        raise NotImplementedError


class EventBase:
    @abstractmethod
    def add_listener(self, listener: Listener) -> None:
        raise NotImplementedError

    @abstractmethod
    def trigger(self, *args, **kwargs) -> None:
        raise NotImplementedError


class Event(EventBase):
    def __init__(self, name: str) -> None:
        self.name = name
        self._listeners = []

    def add_listener(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def trigger(self, *args, **kwargs) -> None:
        for listener in self._listeners:
            listener.notify(*args, **kwargs)


class EventManager:
    _event_does_not_exist_error_message: ClassVar[str] = "Event {event_name} does not exist"

    def __init__(self, events: Mapping[str, EventBase]) -> None:
        self._events = events
        self._logger = logging.getLogger(self.__class__.__name__)

    def add_listener_to_event(self, event_name: str, listener: Listener) -> None:
        if not (event := self._events.get(event_name)):
            raise ValueError(self._event_does_not_exist_error_message.format(event_name=event_name))
        event.add_listener(listener)

    def trigger_event(self, event_name: str, *args, **kwargs) -> None:
        self._logger.debug(f"Triggering event {event_name}...")
        if not (event := self._events.get(event_name)):
            raise ValueError(self._event_does_not_exist_error_message.format(event_name=event_name))
        event.trigger(*args, **kwargs)
        self._logger.info(f"Event {event_name} triggered.")
