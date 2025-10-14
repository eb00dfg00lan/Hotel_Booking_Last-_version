from typing import List, Iterable
from functools import reduce
from core.domain import Hotel, Booking
from datetime import date


def mark_unavailable(hotel: Hotel) -> Hotel:
    return Hotel(**{**hotel.__dict__, "available": False})


def filter_available(hotels: Iterable[Hotel]) -> List[Hotel]:
    return list(filter(lambda h: h.available, hotels))


def total_booking_cost(booking: Booking, hotels: Iterable[Hotel]) -> float:
    total = 0.0
    for item in booking.items:
        hotel = next((h for h in hotels if h.id == item.hotel_id), None)
        if not hotel:
            continue
        nights = (date.fromisoformat(item.checkout) - date.fromisoformat(item.checkin)).days
        total += hotel.price * max(0, nights)
    return total

def total_cost_all(bookings: Iterable[Booking], hotels: Iterable[Hotel]) -> float:
    return sum(total_booking_cost(b, hotels) for b in bookings)
