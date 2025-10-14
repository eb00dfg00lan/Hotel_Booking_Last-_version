import pytest
from core import domain
from types import SimpleNamespace
from core.transforms import filter_available, total_booking_cost, total_cost_all

# Sample data
def sample_hotels():
    return [
        domain.Hotel(id=1, name="Hilton Almaty", stars=5, city="Almaty", features=("Hotel","Spa","Resort")),
        domain.Hotel(id=2, name="Rixos Astana", stars=5, city="Astana", features=("Hotel","Spa","Resort")),
        domain.Hotel(id=3, name="Aksunkar Hotel", stars=4, city="Shymkent", features=("Hotel","Spa","Resort")),
    ]

def sample_cart_item():
    return domain.CartItem(id=1, hotel_id=1, room_type_id=1, rate_id=1,
                           checkin="2025-10-15", checkout="2025-10-17", guests=1)

def sample_booking():
    return domain.Booking(id=1, guest_id=1, items=(sample_cart_item(),), total=0, status="held")

# Tests
def test_hotel_immutable():
    h = sample_hotels()[0]
    with pytest.raises(Exception):
        h.city = "New City"

def test_booking_immutable():
    b = sample_booking()
    with pytest.raises(Exception):
        b.total = 100

def test_filter_available_returns_correct_list():
    hotels = [SimpleNamespace(**h.__dict__, available=True) for h in sample_hotels()]
    hotels[0].available = False
    avail = filter_available(hotels)
    assert len(avail) == 2
    assert all(h.available for h in avail)

def test_total_booking_cost_computation():
    hotels = [SimpleNamespace(**h.__dict__, price=25000) for h in sample_hotels()]
    b = sample_booking()
    cost = total_booking_cost(b, hotels)
    assert cost == 50000  # 2 nights * 25_000

def test_total_cost_all_reduces_sum():
    hotels = [SimpleNamespace(**h.__dict__, price=25000) for h in sample_hotels()]
    b1 = sample_booking()
    b2 = sample_booking()
    total = total_cost_all([b1,b2], hotels)
    assert total == 100000
