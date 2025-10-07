import streamlit as st
from datetime import date, timedelta
from tools.db import fetch_hotels

def render(goto):
    st.title("🔍 Поиск отелей")
    rows = fetch_hotels() or []  # (id, name, city, price, rating, rooms, available)

    cities = sorted({r[2] for r in rows}) if rows else []
    city = st.selectbox("Город", ["Все"] + cities)

    max_price_in_data = max((int(r[3]) for r in rows), default=100000)
    slider_max = max(10000, ((max_price_in_data // 10000) + 1) * 10000)
    colA, colB = st.columns(2)
    with colA:
        max_price = st.slider("Макс. цена (ночь)", 0, slider_max, min(slider_max, 50000))
    with colB:
        min_stars = st.slider("Минимум ⭐", 1, 5, 3)

    items = [
        {"id": int(r[0]), "name": r[1], "city": r[2], "price": int(r[3]),
         "rating": float(r[4]), "rooms": int(r[5]), "available": bool(r[6])}
        for r in rows
    ]
    def match_city(x):  return True if city == "Все" else (x["city"] == city)
    def match_price(x): return x["price"] <= max_price
    def match_stars(x):
        stars = max(1, min(5, int(round(x["rating"]))))
        return stars >= min_stars

    filtered = [x for x in items if match_city(x) and match_price(x) and match_stars(x)]

    if not filtered:
        st.info("Нет отелей по заданным критериям.")
        return

    for h in filtered:
        st.markdown(f"### {h['name']} — {h['city']}")
        stars = max(1, min(5, int(round(h['rating']))))
        st.write(f"Цена: {h['price']} ₸ | ⭐ {stars} | Рейтинг: {h['rating']:.1f} | Номеров: {h['rooms']}")
        if st.button(f"Забронировать {h['name']}", key=f"book_{h['id']}"):
            if not st.session_state.get("user"):
                st.error("Сначала войдите в систему.")
            else:
                st.session_state.selected_hotel_id = h["id"]
                goto("Booking")