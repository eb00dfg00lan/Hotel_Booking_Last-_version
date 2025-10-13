# pages/search_page.py
import streamlit as st
from pathlib import Path
from tools.db import fetch_hotels
from core.filtres import make_city_filter, make_price_range_filter, make_stars_filter, filter_hotels


def load_css(file_path: str):
    css = Path(file_path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render(goto):
    st.title("🔍 Поиск отелей")
    
    load_css("assets/app.css")
    rows = fetch_hotels() or []  # (id, name, city, price, rating, rooms, available)
    load_css("assets/app.css")

    # --- фильтры ---
    st.markdown('<div class="filters-header">⚙️ Фильтры</div>', unsafe_allow_html=True)

    cities = sorted({r[2] for r in rows}) if rows else []
    city = st.selectbox("🏙️ Город", ["Все"] + cities)

    max_price_in_data = max((int(r[3]) for r in rows), default=100000)
    slider_max = max(10000, ((max_price_in_data // 10000) + 1) * 10000)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("💰 **Максимальная цена** (₸/ночь)")
        max_price = st.slider("", 0, slider_max, min(slider_max, 50000), key="price_slider")
    with colB:
        st.markdown("⭐ **Минимальный рейтинг**")
        min_stars = st.slider("", 1, 5, 3, key="stars_slider")
    # --- структура для фильтрации ---
    items = [
        {"id": int(r[0]), "name": r[1], "city": r[2], "price": int(r[3]),
         "rating": float(r[4]), "rooms": int(r[5]), "available": bool(r[6])}
        for r in rows
    ]

    preds = [
        make_city_filter(city),
        make_price_range_filter(0, max_price),
        make_stars_filter(min_stars),
    ]
    filtered = filter_hotels(items, preds)

    # --- вывод ---
    if not filtered:
        st.info("Нет отелей по заданным критериям.")
        return

    for h in filtered:
        stars = max(1, min(5, int(round(h["rating"]))))

        # --- теперь каждый отель в своем expander ---
        with st.expander(f"{h['name']} — {h['city']} ⭐ {stars}", expanded=False):
            st.write(f"**Цена за ночь:** {h['price']} ₸")
            st.write(f"**Рейтинг:** {h['rating']:.1f}")
            st.write(f"**Номеров всего:** {h['rooms']}")
            st.write(f"**Доступно сейчас:** {'✅ Есть' if h['available'] else '❌ Нет'}")

            # кнопка бронирования
            if st.button(f"Забронировать", key=f"book_{h['id']}"):
                if not st.session_state.get("user"):
                    st.error("Сначала войдите в систему.")
                else:
                    st.session_state.selected_hotel_id = h["id"]
                    goto("Booking")
