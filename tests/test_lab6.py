import time
import pytest
from pages.search_page import bus

# вспомогательный handler
def dummy_handler(data):
    pass

def test_delay_single_event():
    bus.subscribers.clear()
    bus.subscribe("test1", dummy_handler)
    start = time.time()
    bus.emit("test1", None)
    end = time.time()
    assert (end - start) >= 0.5

def test_delay_multiple_handlers():
    bus.subscribers.clear()
    bus.subscribe("test2", dummy_handler)
    bus.subscribe("test2", dummy_handler)
    start = time.time()
    bus.emit("test2", None)
    end = time.time()
    assert (end - start) >= 0.5

def test_delay_multiple_events():
    bus.subscribers.clear()
    bus.subscribe("event1", dummy_handler)
    bus.subscribe("event2", dummy_handler)
    start = time.time()
    bus.emit("event1", None)
    bus.emit("event2", None)
    end = time.time()
    assert (end - start) >= 1.0


def test_delay_custom_check():
    bus.subscribers.clear()
    bus.subscribe("test3", dummy_handler)
    start = time.time()
    bus.emit("test3", None)
    end = time.time()
    delay_measured = end - start
    assert delay_measured >= 0.5 and delay_measured < 1.0


def test_delay_real_handler():
    bus.subscribers.clear()
    called = {"flag": False}

    def handler(data):
        called["flag"] = True

    bus.subscribe("test4", handler)
    start = time.time()
    bus.emit("test4", None)
    end = time.time()
    assert called["flag"] == True
    assert (end - start) >= 0.5