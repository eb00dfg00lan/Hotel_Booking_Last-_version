# --- ВВЕРХ ФАЙЛА (импорты и типы) ---
import uuid
from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar, Union, cast
from datetime import date, timedelta
import streamlit as st
from tools.db import fetch_hotels, insert_booking
from datetime import date
from typing import Callable, Generic, TypeVar, Union, Dict

A = TypeVar("A"); B = TypeVar("B"); E = TypeVar("E")
# Совместимость: короткие конструкторы
def Right(value):
    return Either.right(value)

def Left(error):
    return Either.left(error)


@dataclass(frozen=True)
class Maybe(Generic[A]):
    value: Optional[A] = None
    def is_none(self) -> bool: return self.value is None
    def map(self, fn: Callable[[A], B]) -> "Maybe[B]":
        return Maybe(None) if self.is_none() else Maybe(fn(cast(A, self.value)))
    def bind(self, fn: Callable[[A], "Maybe[B]"]) -> "Maybe[B]":
        return Maybe(None) if self.is_none() else fn(cast(A, self.value))
    def get_or_else(self, default: B | A) -> A | B:
        return self.value if not self.is_none() else default

@dataclass(frozen=True)
class Either(Generic[E, A]):
    is_right: bool
    value: Union[E, A]
    @staticmethod
    def right(value: A) -> "Either[E, A]": return Either(True, value)
    @staticmethod
    def left(error: E) -> "Either[E, A]":  return Either(False, error)
    def map(self, fn: Callable[[A], B]) -> "Either[E, B]":
        if not self.is_right: return cast(Either[E, B], self)
        return Either.right(fn(cast(A, self.value)))
    def bind(self, fn: Callable[[A], "Either[E, B]"]) -> "Either[E, B]":
        if not self.is_right: return cast(Either[E, B], self)
        return fn(cast(A, self.value))
    def get_or_else(self, default: B | A) -> A | B:
        return self.value if self.is_right else default

# ---- доменная модель и проверки ----
@dataclass(frozen=True)
class Booking:
    user_id: int
    hotel_id: int
    check_in: date
    check_out: date
    guests: int
    nightly_price: int  # цена за ночь

def validate_booking(b: Booking) -> Either[dict, Booking]:
    if b.check_in >= b.check_out:
        return Either.left({"date": "check_in must be < check_out"})
    if (b.check_out - b.check_in).days <= 0:
        return Either.left({"nights": "минимум 1 ночь"})
    if b.guests <= 0:
        return Either.left({"guests": "гостей должно быть ≥ 1"})
    return Either.right(b)

def quote_amount(b: Booking) -> int:
    nights = (b.check_out - b.check_in).days
    return b.nightly_price * nights

def _make_tx_key(b: Booking) -> str:
    # Идемпотентный ключ для защиты от двойной записи
    return f"{b.user_id}:{b.hotel_id}:{b.check_in.isoformat()}:{b.check_out.isoformat()}:{b.guests}"
@dataclass(frozen=True)
class BookingDraft:
    user_id: int
    hotel_id: int
    check_in: date
    check_out: date
    guests: int
    nightly_price: int  # базовая цена за ночь

def validate_booking(b: BookingDraft) -> Either[Dict, BookingDraft]:
    errors: Dict[str, str] = {}
    if b.check_in >= b.check_out:
        errors["dates"] = "Дата выезда должна быть позже даты заезда."
    if b.guests <= 0:
        errors["guests"] = "Число гостей должно быть ≥ 1."
    nights = (b.check_out - b.check_in).days
    if nights <= 0:
        errors["nights"] = "Ночей должно быть ≥ 1."
    if b.nightly_price <= 0:
        errors["price"] = "Цена за ночь должна быть > 0."

    # тут можно добавить min/max stay, capacity и т.п.
    return Right(b) if not errors else Left(errors)