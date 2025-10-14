import pytest
from types import SimpleNamespace

def count_bookings(bookings, i=0):
    return len(bookings)

def sum_guests(bookings, i=0):
    return sum(getattr(b, "guests", 0) for b in bookings)

def sample_booking(guests=1):
    return SimpleNamespace(guests=guests)


def test_count_bookings_1():
    bookings = [1,2,3]
    assert count_bookings(tuple(bookings)) == 3

def test_count_bookings_2():
    bookings = []
    assert count_bookings(tuple(bookings)) == 0

def test_count_bookings_3():
    bookings = [1]
    assert count_bookings(tuple(bookings)) == 1

def test_sum_guests_1():
    bookings = [sample_booking(2), sample_booking(3)]
    assert sum_guests(tuple(bookings)) == 5

def test_sum_guests_2():
    bookings = [sample_booking(4), sample_booking(1), sample_booking(5)]
    assert sum_guests(tuple(bookings)) == 10

