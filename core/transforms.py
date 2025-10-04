from typing import List, Iterable
from functools import reduce
from core.domain import Hotel, Booking
from datetime import date


def mark_unavailable(hotel: Hotel) -> Hotel:
    return Hotel(**{**hotel.__dict__, "available": False})


def filter_available(hotels: Iterable[Hotel]) -> List[Hotel]:
    return list(filter(lambda h: h.available, hotels))


def total_booking_cost(booking: Booking, hotels: Iterable[Hotel]) -> float:
    hotel = next((h for h in hotels if h.id == booking.hotel_id), None)
    if not hotel:
        return 0.0
    nights = (booking.check_out - booking.check_in).days
    return hotel.price * max(0, nights)


def total_cost_all(bookings: Iterable[Booking], hotels: Iterable[Hotel]) -> float:
    costs = map(lambda b: total_booking_cost(b, hotels), bookings)
    return reduce(lambda a, b: a + b, costs, 0.0)
