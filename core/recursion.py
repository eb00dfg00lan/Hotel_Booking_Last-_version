from functools import lru_cache
from typing import List
from core.domain import Booking, Hotel
from datetime import date


def count_bookings(bookings: List[Booking], i: int = 0) -> int:
    if i >= len(bookings):
        return 0
    return 1 + count_bookings(bookings, i + 1)


def sum_guests(bookings: List[Booking], i: int = 0) -> int:
    if i >= len(bookings):
        return 0
    return bookings[i].guests + sum_guests(bookings, i + 1)

@lru_cache(maxsize=None)
def days_between(y1: int, m1: int, d1: int, y2: int, m2: int, d2: int) -> int:
    d1_obj = date(y1, m1, d1)
    d2_obj = date(y2, m2, d2)
    return abs((d2_obj - d1_obj).days)


def booking_days(booking):
    return days_between(booking.check_in.year, booking.check_in.month, booking.check_in.day, booking.check_out.year, booking.check_out.month, booking.check_out.day)
