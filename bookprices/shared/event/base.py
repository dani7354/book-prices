from abc import abstractmethod
from typing import Mapping, ClassVar


class Listener:
    @abstractmethod
    def notify(self, *args, **kwargs):
        raise NotImplementedError


class Event:
    def __init__(self, name) -> None:
        self.name = name
        self._listeners = []

    def add_listener(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def trigger(self, *args, **kwargs) -> None:
        for listener in self._listeners:
            listener.notify(*args, **kwargs)


class EventManager:
    _event_does_not_exist_error_message: ClassVar[str] = "Event {event_name} does not exist"

    def __init__(self, events: Mapping[str, Event]) -> None:
        self._events = events

    def add_listener_to_event(self, event_name: str, listener: Listener) -> None:
        if not (event := self._events.get(event_name)):
            raise ValueError(self._event_does_not_exist_error_message.format(event_name=event_name))
        event.add_listener(listener)

    def trigger_event(self, event_name: str, *args, **kwargs) -> None:
        if not (event := self._events.get(event_name)):
            raise ValueError(self._event_does_not_exist_error_message.format(event_name=event_name))
        event.trigger(*args, **kwargs)
