from __future__ import annotations
from collections import defaultdict
from typing import Dict, Iterable
from core.domain import Price, Availability, RatePlan, RoomType, Hotel

def index_prices_by_rate_date(prices: Iterable[Price]) -> Dict[tuple[int, str], int]:
    # (rate_id, 'YYYY-MM-DD') -> amount
    idx: Dict[tuple[int, str], int] = {}
    for p in prices:
        idx[(p.rate_id, p.date)] = p.amount
    return idx

def index_avail_by_rt_date(avails: Iterable[Availability]) -> Dict[tuple[int, str], int]:
    # (room_type_id, 'YYYY-MM-DD') -> available
    idx: Dict[tuple[int, str], int] = {}
    for a in avails:
        idx[(a.room_type_id, a.date)] = a.available
    return idx

def index_rates_by_id(rates: Iterable[RatePlan]) -> Dict[int, RatePlan]:
    return {r.id: r for r in rates}

def index_roomtypes_by_id(room_types: Iterable[RoomType]) -> Dict[int, RoomType]:
    return {rt.id: rt for rt in room_types}

def index_hotels_by_id(hotels: Iterable[Hotel]) -> Dict[int, Hotel]:
    return {h.id: h for h in hotels}

def index_prices_by_rate(prices: Iterable[Price]) -> Dict[int, list[Price]]:
    d: Dict[int, list[Price]] = defaultdict(list)
    for p in prices:
        d[p.rate_id].append(p)
    for rid in d:
        d[rid].sort(key=lambda x: x.date)
    return d
