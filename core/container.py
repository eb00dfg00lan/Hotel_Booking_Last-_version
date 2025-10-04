from dataclasses import dataclass
from typing import Generic, TypeVar, Callable, Union

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Maybe(Generic[T]):
    value: T = None

    def is_none(self) -> bool:
        return self.value is None

    def map(self, fn: Callable[[T], U]) -> "Maybe[U]":
        if self.is_none():
            return Maybe(None)
        return Maybe(fn(self.value))

    def get_or_else(self, default: U):
        return default if self.is_none() else self.value


@dataclass(frozen=True)
class Either(Generic[T, U]):
    is_right: bool
    value: Union[T, U]

    @staticmethod
    def right(value):
        return Either(True, value)

    @staticmethod
    def left(value):
        return Either(False, value)

    def map(self, fn: Callable[[T], U]) -> "Either":
        if not self.is_right:
            return self
        return Either.right(fn(self.value))

    def get_or_else(self, default):
        return self.value if self.is_right else default
