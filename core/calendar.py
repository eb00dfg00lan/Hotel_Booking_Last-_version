from __future__ import annotations
from typing import Tuple, Optional, List, NamedTuple
from functools import lru_cache
from datetime import date, timedelta

from core.domain import Price, Availability, Rule
from core.dates import month_grid_bounds, to_iso
from core.indexes import index_prices_by_rate_date, index_avail_by_rt_date
from core.rules import is_cta_date, is_ctd_date

class DayCell(NamedTuple):
    d_iso: str
    amount: Optional[int]       # None — цены нет
    available: bool             # остаток > 0
    flags: tuple[str, ...]      # ('cta','ctd','soldout')

@lru_cache(maxsize=512)
def build_price_calendar(
    room_type_id: int,
    rate_id: int,
    month_start: date,
    prices: Tuple[Price, ...],
    avails: Tuple[Availability, ...],
    rules: Tuple[Rule, ...],
) -> List[List[DayCell]]:
    p_idx = index_prices_by_rate_date(prices)
    a_idx = index_avail_by_rt_date(avails)

    start, end = month_grid_bounds(month_start)
    days_total = (end - start).days

    grid: List[List[DayCell]] = []
    row: List[DayCell] = []
    cur = start

    for _ in range(days_total):
        iso = to_iso(cur)
        amount = p_idx.get((rate_id, iso))
        left = a_idx.get((room_type_id, iso), 0)
        available = left > 0

        flags: list[str] = []
        if is_cta_date(rules, room_type_id, rate_id, iso):
            flags.append("cta")
        if is_ctd_date(rules, room_type_id, rate_id, iso):
            flags.append("ctd")
        if not available:
            flags.append("soldout")

        row.append(DayCell(iso, amount, available, tuple(flags)))

        if len(row) == 7:
            grid.append(row)
            row = []
        cur += timedelta(days=1)

    if row:
        grid.append(row)
    return grid
