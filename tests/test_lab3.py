import pytest
from functools import lru_cache


@lru_cache(maxsize=None)
def expensive(x):
    return x * 2


def test_expensive_1():
    assert expensive(2) == 4

def test_expensive_2():
    assert expensive(5) == 10

def test_expensive_3():
    assert expensive(0) == 0

def test_expensive_4():
    assert expensive(100) == 200

def test_expensive_5():
    assert expensive(7) == 14
