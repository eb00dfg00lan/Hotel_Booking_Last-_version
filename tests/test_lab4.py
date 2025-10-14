import pytest

class Maybe:
    def __init__(self, value=None):
        self.value = value
    def is_none(self):
        return self.value is None
    def map(self, fn):
        return Maybe(fn(self.value)) if self.value is not None else Maybe(None)
    def get_or_else(self, default):
        return self.value if self.value is not None else default

class Either:
    def __init__(self, is_right, value):
        self.is_right = is_right
        self.value = value
    @staticmethod
    def right(value):
        return Either(True, value)
    @staticmethod
    def left(value):
        return Either(False, value)
    def map(self, fn):
        if not self.is_right:
            return self
        return Either.right(fn(self.value))
    def get_or_else(self, default):
        return self.value if self.is_right else default


def test_maybe_1():
    m = Maybe(5)
    assert m.map(lambda x: x*2).get_or_else(0) == 10

def test_maybe_2():
    m = Maybe()
    assert m.get_or_else(0) == 0

def test_maybe_3():
    m = Maybe("hi")
    assert m.map(lambda x: x.upper()).get_or_else("") == "HI"


def test_either_1():
    e = Either.right(5)
    assert e.map(lambda x: x*3).get_or_else(0) == 15

def test_either_2():
    e = Either.left("error")
    assert e.get_or_else(0) == 0
