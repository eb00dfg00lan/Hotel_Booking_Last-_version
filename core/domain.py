from dataclasses import dataclass
from typing import Tuple, Optional, Dict

@dataclass(frozen=True)
class Hotel:
    id: int
    name: str
    stars: int
    city: str
    features: Tuple[str, ...]

@dataclass(frozen=True)
class RoomType:
    id: int
    hotel_id: int
    name: str
    capacity: int
    beds: Tuple[str, ...]
    features: Tuple[str, ...]

@dataclass(frozen=True)
class RatePlan:
    id: int
    hotel_id: int
    room_type_id: int
    title: str
    meal: str
    refundable: bool
    cancel_before_days: Optional[int]

@dataclass(frozen=True)
class Price:
    id: int
    rate_id: int
    date: str
    amount: int
    currency: str

@dataclass(frozen=True)
class Availability:
    id: int
    room_type_id: int
    date: str
    available: int

@dataclass(frozen=True)
class Guest:
    id: int
    name: str
    email: str

@dataclass(frozen=True)
class CartItem:
    id: int
    hotel_id: int
    room_type_id: int
    rate_id: int
    checkin: str
    checkout: str
    guests: int

@dataclass(frozen=True)
class Booking:
    id: int
    guest_id: int
    items: Tuple[CartItem, ...]
    total: int
    status: str  # held/confirmed/cancelled

@dataclass(frozen=True)
class Payment:
    id: int
    booking_id: int
    amount: int
    ts: str
    method: str

@dataclass(frozen=True)
class Event:
    id: int
    ts: str
    name: str
    payload: Dict

@dataclass(frozen=True)
class Rule:
    id: int
    kind: str
    payload: Dict
