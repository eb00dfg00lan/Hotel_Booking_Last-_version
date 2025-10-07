# core/filtres.py
from typing import Any, Callable, Sequence, Iterable

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
    # если нет поля stars — считаем из rating (округление и ограничение 1..5)
    def _ok(h: Any) -> bool:
        stars = _get(h, "stars", None)
        if stars is None:
            rating = float(_get(h, "rating", 0.0))
            stars = max(1, min(5, int(round(rating))))
        return int(stars) >= int(min_stars)
    return _ok

def filter_hotels(items: Sequence[Any], preds: Sequence[Predicate]) -> list:
    if not preds:
        return list(items)
    return [h for h in items if all(p(h) for p in preds)]
