# pages/search_page.py
import streamlit as st
import json
from pathlib import Path
from tools.db import fetch_hotels
from core.filtres import make_city_filter, make_price_range_filter, make_stars_filter, filter_hotels

ROOMTYPE_FIXED = [
    "Standard",
    "Standard Plus",
    "Standard Deluxe",
    "VIP Standard",
    "VIP Plus",
    "VIP Deluxe",
]
EXTRAS = ["Breakfast","Lunch","Dinner","Bar","Drinks","SPA","Pool","Wi-Fi","Parking"]

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
    st.markdown("""
    <style>
    /* Основной контейнер Streamlit */
    html, body, [class*="stApp"] {
        background-color: black !important; /* чёрный фон */
        color: white;
        position: relative;
        z-index: 0; /* нейтральный уровень — не перекрывает кнопки */
    }

    /* Отдельный фоновый слой — без отрицательного z-index */
    .bg-layer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: black;
        z-index: 0; /* просто на заднем плане, но не отрицательно */
    }
    </style>

    <div class="bg-layer"></div>
    """, unsafe_allow_html=True)
    st.title("Search Hotels")
    load_css("assets/app.css")

    # rows: id, name, city, price, rating, rooms, available, roomtype, rateplan, owner_id
    rows = fetch_hotels() or []

    # базовые фильтры
    st.markdown('<div class="filters-header">⚙️ Filters</div>', unsafe_allow_html=True)
    cities = sorted({r[2] for r in rows}) if rows else []
    city = st.selectbox("🏙️ City", ["All"] + cities)

    max_price_in_data = max((int(r[3]) for r in rows), default=100000)
    slider_max = max(10000, ((max_price_in_data // 10000) + 1) * 10000)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("💰 **Max Price** (₸/night)")
        max_price = st.slider("", 0, slider_max, min(slider_max, 50000), key="price_slider")
    with colB:
        st.markdown("⭐ **Min Rating**")
        min_stars = st.slider("", 1, 5, 3, key="stars_slider")

    # Типы номеров (roomtype)
    with st.expander("Room Types", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            rt_std       = st.checkbox("Standard", key="rt_std")
            rt_std_plus  = st.checkbox("Standard Plus", key="rt_std_plus")
        with col2:
            rt_std_delux = st.checkbox("Standard Deluxe", key="rt_std_delux")
            rt_vip_std   = st.checkbox("VIP Standard", key="rt_vip_std")
        with col3:
            rt_vip_plus  = st.checkbox("VIP Plus", key="rt_vip_plus")
            rt_vip_delux = st.checkbox("VIP Deluxe", key="rt_vip_delux")
        rt_mode = st.radio("Room Type Match", ["Any", "All"], horizontal=True, key="rt_mode")
        selected_roomtypes = [
            name for flag, name in [
                (rt_std, "Standard"),
                (rt_std_plus, "Standard Plus"),
                (rt_std_delux, "Standard Deluxe"),
                (rt_vip_std, "VIP Standard"),
                (rt_vip_plus, "VIP Plus"),
                (rt_vip_delux, "VIP Deluxe"),
            ] if flag
        ]

    # Доп-услуги (rateplan)
    with st.expander("More Services", expanded=True):
        c1, c2, c3 = st.columns(3)
        flags = {}
        for idx, name in enumerate(EXTRAS):
            with (c1 if idx % 3 == 0 else c2 if idx % 3 == 1 else c3):
                flags[name] = st.checkbox(name, key=f"rp_{_norm(name)}")
        rp_mode = st.radio("More Services", ["Any", "All"], horizontal=True, key="rp_mode")
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
        st.info("No hotels found matching your criteria.")
        return

    for h in filtered:
        stars = max(1, min(5, int(round(h["rating"]))))
        with st.expander(f"{h['name']} — {h['city']} ⭐ {stars}", expanded=False):
            st.write(f"**Price to this night:** {h['price']} ₸")
            st.write(f"**Rating:** {h['rating']:.1f}")
            st.write(f"**Total Rooms:** {h['rooms']}")
            st.write(f"**Available Now:** {'✅ Yes' if h['available'] else '❌ No'}")
            if h.get("roomtype_list"):
                st.write("**Room Types:** " + ", ".join(sorted(set(h["roomtype_list"]))))
            if h.get("rateplan_list"):
                st.write("**More Services:** " + ", ".join(sorted(set(h["rateplan_list"]))))

            if st.button("Book Now", key=f"book_{h['id']}"):
                if not st.session_state.get("user"):
                    st.error("Please log in first.")
                else:
                    st.session_state.selected_hotel_id = h["id"]
                    goto("Booking")
