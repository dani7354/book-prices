from bookprices.shared.event.base import Listener


class TestListener(Listener):
    def __init__(self):
        self._notified = False
        self._args = None
        self._kwargs = None

    def notify(self, *args, **kwargs):
        self._notified = True
        self._args = args
        self._kwargs = kwargs