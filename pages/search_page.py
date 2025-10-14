# pages/search_page.py
import streamlit as st
import json
from pathlib import Path
from tools.db import fetch_hotels
from core.filtres import make_city_filter, make_price_range_filter, make_stars_filter, filter_hotels

ROOMTYPE_FIXED = [
    "Стандарт",
    "Стандарт плюс",
    "Стандарт делюкс",
    "VIP стандарт",
    "VIP плюс",
    "VIP делюкс",
]
EXTRAS = ["Завтрак","Обед","Ужин","Бар","Напитки","SPA","Бассейн","Wi-Fi","Парковка"]

def _parse_list_field(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        try:
            v = json.loads(s)
            if isinstance(v, list):
                return [str(x).strip() for x in v if str(x).strip()]
            if isinstance(v, dict):
                return [str(k).strip() for k in v.keys() if str(k).strip()]
        except Exception:
            pass
        return [t.strip() for t in s.split(",") if t.strip()]
    return [str(raw).strip()] if str(raw).strip() else []

def _norm(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())

def _make_name_presence_filter(list_key: str, selected: list[str], require_all: bool):
    pats = [_norm(x) for x in (selected or []) if x and x.strip()]
    def pred(h: dict) -> bool:
        if not pats:
            return True
        vals = [_norm(x) for x in h.get(list_key, [])]
        if require_all:
            return all(any(p == v or p in v for v in vals) for p in pats)
        return any(any(p == v or p in v for v in vals) for p in pats)
    return pred

def load_css(path: str):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render(goto):
    st.title("🔍 Поиск отелей")
    load_css("assets/app.css")

    # rows: id, name, city, price, rating, rooms, available, roomtype, rateplan, owner_id
    rows = fetch_hotels() or []

    # базовые фильтры
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

    # Типы номеров (roomtype)
    with st.expander("Типы номеров", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            rt_std       = st.checkbox("Стандарт", key="rt_std")
            rt_std_plus  = st.checkbox("Стандарт плюс", key="rt_std_plus")
        with col2:
            rt_std_delux = st.checkbox("Стандарт делюкс", key="rt_std_delux")
            rt_vip_std   = st.checkbox("VIP стандарт", key="rt_vip_std")
        with col3:
            rt_vip_plus  = st.checkbox("VIP плюс", key="rt_vip_plus")
            rt_vip_delux = st.checkbox("VIP делюкс", key="rt_vip_delux")
        rt_mode = st.radio("Совпадение типов", ["Любой", "Все"], horizontal=True, key="rt_mode")
        selected_roomtypes = [
            name for flag, name in [
                (rt_std, "Стандарт"),
                (rt_std_plus, "Стандарт плюс"),
                (rt_std_delux, "Стандарт делюкс"),
                (rt_vip_std, "VIP стандарт"),
                (rt_vip_plus, "VIP плюс"),
                (rt_vip_delux, "VIP делюкс"),
            ] if flag
        ]

    # Доп-услуги (rateplan)
    with st.expander("Дополнительные услуги", expanded=True):
        c1, c2, c3 = st.columns(3)
        flags = {}
        for idx, name in enumerate(EXTRAS):
            with (c1 if idx % 3 == 0 else c2 if idx % 3 == 1 else c3):
                flags[name] = st.checkbox(name, key=f"rp_{_norm(name)}")
        rp_mode = st.radio("Совпадение услуг", ["Любая", "Все"], horizontal=True, key="rp_mode")
        selected_extras = [name for name, f in flags.items() if f]

    # подготовка данных
    items = []
    for r in rows:
        roomtype_list = _parse_list_field(r[7])
        rateplan_list = _parse_list_field(r[8])
        items.append({
            "id": int(r[0]),
            "name": r[1],
            "city": r[2],
            "price": int(r[3]),
            "rating": float(r[4]),
            "rooms": int(r[5]),
            "available": bool(r[6]),
            "roomtype_list": roomtype_list,
            "rateplan_list": rateplan_list,  # теперь это именно услуги
        })

    preds = [
        make_city_filter(city),
        make_price_range_filter(0, max_price),
        make_stars_filter(min_stars),
        _make_name_presence_filter("roomtype_list", selected_roomtypes, require_all=(rt_mode == "Все")),
        _make_name_presence_filter("rateplan_list", selected_extras, require_all=(rp_mode == "Все")),
    ]

    filtered = filter_hotels(items, preds)

    if not filtered:
        st.info("Нет отелей по заданным критериям. Попробуйте снять часть фильтров (типы/услуги).")
        return

    for h in filtered:
        stars = max(1, min(5, int(round(h["rating"]))))
        with st.expander(f"{h['name']} — {h['city']} ⭐ {stars}", expanded=False):
            st.write(f"**Цена за ночь:** {h['price']} ₸")
            st.write(f"**Рейтинг:** {h['rating']:.1f}")
            st.write(f"**Номеров всего:** {h['rooms']}")
            st.write(f"**Доступно сейчас:** {'✅ Есть' if h['available'] else '❌ Нет'}")
            if h.get("roomtype_list"):
                st.write("**Типы номеров:** " + ", ".join(sorted(set(h["roomtype_list"]))))
            if h.get("rateplan_list"):
                st.write("**Доп. услуги:** " + ", ".join(sorted(set(h["rateplan_list"]))))

            if st.button("Забронировать", key=f"book_{h['id']}"):
                if not st.session_state.get("user"):
                    st.error("Сначала войдите в систему.")
                else:
                    st.session_state.selected_hotel_id = h["id"]
                    goto("Booking")
