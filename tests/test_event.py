import pytest

from bookprices.shared.event.base import Event, EventManager
from tests.fake.event import TestListener


def test_event_manager_trigger_event_no_args_succeeds() -> None:
    event = Event("test_event")
    listener = TestListener()
    event.add_listener(listener)
    event_manager = EventManager({event.name: event})

    event_manager.trigger_event(event.name)

    assert listener._notified


def test_event_manager_trigger_invalid_event_fails() -> None:
    event = Event("test_event")
    listener = TestListener()
    event.add_listener(listener)
    event_manager = EventManager({event.name: event})

    with pytest.raises(ValueError):
        event_manager.trigger_event("another_event")

    assert not listener._notified


def test_event_manager_trigger_event_with_args_succeeds() -> None:
    event = Event("test_event")
    listener = TestListener()
    event.add_listener(listener)
    event_manager = EventManager({event.name: event})

    args = (1, 2, 3)
    kwargs = {"key": "value", "another_key": "another_value"}

    event_manager.trigger_event(event.name, *args, **kwargs)

    assert listener._notified
    assert listener._args == args
    assert listener._kwargs == kwargs
