from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Hotel:
    id: int
    name: str
    city: str
    price: float
    rating: float
    rooms: int
    available: bool


@dataclass(frozen=True)
class User:
    id: int
    username: str
    email: str
    password: str  


@dataclass(frozen=True)
class Booking:
    id: int
    user_id: int
    hotel_id: int
    check_in: date
    check_out: date
    guests: int
