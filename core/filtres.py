from typing import Callable, Iterable, List
from core.domain import Hotel


def make_city_filter(city: str) -> Callable[[Hotel], bool]:
    target = city.strip().lower()
    def predicate(h: Hotel) -> bool:
        return h.city.strip().lower() == target
    return predicate


def make_price_range_filter(min_price: float = 0.0, max_price: float = float("inf")) -> Callable[[Hotel], bool]:
    def predicate(h: Hotel) -> bool:
        return (h.price >= min_price) and (h.price <= max_price)
    return predicate


def combine_filters(*preds: Callable[[Hotel], bool]) -> Callable[[Hotel], bool]:
    def combined(h: Hotel) -> bool:
        return all(pred(h) for pred in preds)
    return combined


def filter_hotels(hotels: Iterable[Hotel], predicate: Callable[[Hotel], bool]) -> List[Hotel]:
    return list(filter(predicate, hotels))

def