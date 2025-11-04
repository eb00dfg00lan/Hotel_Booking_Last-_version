from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import Iterator

ISO_FMT = "%Y-%m-%d"

def to_date(s: str) -> date:
    return datetime.strptime(s, ISO_FMT).date()

def to_iso(d: date) -> str:
    return d.strftime(ISO_FMT)

def daterange(d1: date, d2: date) -> Iterator[date]:
    """ полуинтервал [d1, d2) — правая граница исключена """
    cur = d1
    while cur < d2:
        yield cur
        cur += timedelta(days=1)

def first_day_of_month(d: date) -> date:
    return d.replace(day=1)

def month_grid_bounds(month_start: date) -> tuple[date, date]:
    """Вернёт (grid_start, grid_end_exclusive) для сетки 6 недель."""
    grid_start = month_start - timedelta(days=month_start.weekday())  # понедельник
    days_total = 42  # 6 недель * 7
    grid_end = grid_start + timedelta(days=days_total)
    return grid_start, grid_end
