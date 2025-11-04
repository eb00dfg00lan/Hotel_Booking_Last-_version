from __future__ import annotations
from typing import Iterable, Iterator, Callable, Dict, Any, Optional, Tuple
from datetime import date, timedelta

from core.domain import Hotel, RoomType, RatePlan, Price, Availability, Rule
from core.dates import to_date, to_iso, daterange
from core.indexes import (
    index_hotels_by_id, index_roomtypes_by_id, index_rates_by_id,
    index_prices_by_rate, index_avail_by_rt_date, index_prices_by_rate_date,
)
from core.rules import get_min_stay, get_max_stay, is_cta_date, is_ctd_date

def iter_available_days(avail: Iterable[Availability], room_type_id: int) -> Iterator[tuple[str, int]]:
    for a in sorted(avail, key=lambda x: x.date):
        if a.room_type_id == room_type_id and a.available > 0:
            yield (a.date, a.available)

def lazy_offers(
    hotels: Iterable[Hotel],
    room_types: Iterable[RoomType],
    rates: Iterable[RatePlan],
    prices: Iterable[Price],
    avails: Iterable[Availability],
    predicate: Callable[[Dict[str, Any]], bool],
    lookahead_days: int = 60,
) -> Iterator[tuple[Hotel, RoomType, RatePlan, int]]:
    H = index_hotels_by_id(hotels)
    RT = index_roomtypes_by_id(room_types)
    P_by_rate = index_prices_by_rate(prices)
    A = index_avail_by_rt_date(avails)

    today = date.today()
    window = {to_iso(today + timedelta(days=i)) for i in range(lookahead_days)}

    for rp in rates:
        h = H.get(rp.hotel_id)
        rt = RT.get(rp.room_type_id)
        if not h or not rt:
            continue

        best: Optional[int] = None
        for p in P_by_rate.get(rp.id, []):
            if p.date in window and A.get((rt.id, p.date), 0) > 0:
                best = p.amount if best is None else min(best, p.amount)

        if best is None:
            continue

        meta = {
            "hotel_id": h.id, "hotel_stars": h.stars, "hotel_city": h.city,
            "room_type_id": rt.id, "rate_id": rp.id,
            "meal": rp.meal, "refundable": rp.refundable,
            "min_price_in_window": best,
        }
        if predicate(meta):
            yield (h, rt, rp, best)

def quote_offer(
    rate_id: int,
    room_type_id: int,
    checkin_iso: str,
    checkout_iso: str,
    prices: Iterable[Price],
    avails: Iterable[Availability],
    rules: Iterable[Rule],
) -> tuple[int, bool, list[str]]:
    p_idx = index_prices_by_rate_date(prices)
    a_idx = index_avail_by_rt_date(avails)

    d1 = to_date(checkin_iso)
    d2 = to_date(checkout_iso)
    days = list(daterange(d1, d2))
    nights = len(days)

    problems: list[str] = []

    min_stay = get_min_stay(rules, room_type_id, rate_id)
    max_stay = get_max_stay(rules, room_type_id, rate_id)
    if nights < min_stay:
        problems.append(f"min_stay {min_stay}")
    if nights > max_stay:
        problems.append(f"max_stay {max_stay}")

    if is_cta_date(rules, room_type_id, rate_id, checkin_iso):
        problems.append("CTA (запрет заезда)")
    if is_ctd_date(rules, room_type_id, rate_id, checkout_iso):
        problems.append("CTD (запрет выезда)")

    total = 0
    for d in days:
        iso = to_iso(d)
        amount = p_idx.get((rate_id, iso))
        if amount is None:
            problems.append(f"Нет цены на {iso}")
            continue
        total += amount

        if a_idx.get((room_type_id, iso), 0) <= 0:
            problems.append(f"Нет доступности на {iso}")

    ok = len(problems) == 0
    return total, ok, problems
