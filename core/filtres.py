# core/filtres.py
from typing import Any, Callable, Iterable, Iterator, Sequence, Dict, List
# Если у тебя Python >=3.9, можно использовать dict[str,int] и list[str], но для совместимости я использую typing.

Predicate = Callable[[Any], bool]

def _get(h: Any, key: str, default=None):
    if isinstance(h, dict):
        return h.get(key, default)
    return getattr(h, key, default)

def make_city_filter(city: str) -> Predicate:
    if not city or city == "Все":
        return lambda h: True
    return lambda h: _get(h, "city") == city

def make_price_range_filter(min_price: int, max_price: int) -> Predicate:
    return lambda h: int(_get(h, "price", 0)) <= int(max_price) and int(_get(h, "price", 0)) >= int(min_price)

def make_stars_filter(min_stars: int) -> Predicate:
    def _ok(h: Any) -> bool:
        stars = _get(h, "stars", None)
        if stars is None:
            try:
                rating = float(_get(h, "rating", 0.0))
            except (TypeError, ValueError):
                rating = 0.0
            # округление к ближайшему, затем ограничение 1..5
            stars = max(1, min(5, int(round(rating))))
        return int(stars) >= int(min_stars)
    return _ok

def filter_hotels(items: Iterable[Any], preds: Sequence[Predicate]) -> Iterator[Any]:
    """
    Лениво фильтрует items через все предикаты.
    Возвращает генератор (итератор), не список.
    Используй list(filter_hotels(...)) только на финальном шаге.
    """
    if not preds:
        # просто итератор по items
        for h in items:
            yield h
        return

    for h in items:
        ok = True
        for p in preds:
            if not p(h):
                ok = False
                break
        if ok:
            yield h

def _make_roomtype_filter(demand: Dict[str, int]):
    """
    demand: { "Стандарт": N, "VIP делюкс": M, ... }
    Оставляем отели, у которых count >= N для каждого выбранного (N>0) типа.
    """
    # очищаем нули
    demand = {k: int(v) for k, v in (demand or {}).items() if int(v) > 0}

    def pred(h: dict) -> bool:
        if not demand:
            return True
        rto = (h.get("roomtype_obj") or {}) if isinstance(h, dict) else getattr(h, "roomtype_obj", {}) or {}
        for k, need in demand.items():
            have = int((rto.get(k) or {}).get("count", 0))
            if have < need:
                return False
        return True

    return pred


def _make_rateplan_filter(required_keys: List[str]):
    """
    required_keys: список ключей из JSON rateplan (breakfast, spa, ...),
    которые пользователь отметил. Все должны быть has=True.
    """
    required_keys = [k for k in (required_keys or []) if k]

    def pred(h: dict) -> bool:
        if not required_keys:
            return True
        rp = (h.get("rateplan_obj") or {}) if isinstance(h, dict) else getattr(h, "rateplan_obj", {}) or {}
        for k in required_keys:
            if not (rp.get(k) or {}).get("has", False):
                return False
        return True

    return pred
