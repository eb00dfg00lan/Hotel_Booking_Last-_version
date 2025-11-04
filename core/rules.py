from __future__ import annotations
from typing import Iterable
from core.domain import Rule

# ожидаемый payload:
# - {"kind":"min_stay", "payload":{"room_type_id":int,"rate_id":int,"value":int}}, и т.п.

def _match(payload: dict, **conds) -> bool:
    for k, v in conds.items():
        if v is None:
            continue
        if payload.get(k) != v:
            return False
    return True

def get_min_stay(rules: Iterable[Rule], room_type_id: int, rate_id: int) -> int:
    best = 1
    for r in rules:
        if r.kind == "min_stay" and _match(r.payload, room_type_id=room_type_id, rate_id=rate_id):
            try:
                val = int(r.payload.get("value", 1))
                if val > best:
                    best = val
            except Exception:
                pass
    return best

def get_max_stay(rules: Iterable[Rule], room_type_id: int, rate_id: int) -> int:
    best = 365
    for r in rules:
        if r.kind == "max_stay" and _match(r.payload, room_type_id=room_type_id, rate_id=rate_id):
            try:
                val = int(r.payload.get("value", 365))
                if val < best:
                    best = val
            except Exception:
                pass
    return best

def is_cta_date(rules: Iterable[Rule], room_type_id: int, rate_id: int, iso_date: str) -> bool:
    for r in rules:
        if r.kind == "cta" and _match(r.payload, room_type_id=room_type_id, rate_id=rate_id, date=iso_date):
            return bool(r.payload.get("value", True))
    return False

def is_ctd_date(rules: Iterable[Rule], room_type_id: int, rate_id: int, iso_date: str) -> bool:
    for r in rules:
        if r.kind == "ctd" and _match(r.payload, room_type_id=room_type_id, rate_id=rate_id, date=iso_date):
            return bool(r.payload.get("value", True))
    return False
