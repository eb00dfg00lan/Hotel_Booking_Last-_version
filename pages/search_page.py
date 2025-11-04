# pages/search_page.py
import json
from pathlib import Path
from datetime import date, timedelta
from urllib.parse import urlencode

import streamlit as st

from tools.db import fetch_hotels
from core.filtres import (
    make_city_filter,
    make_price_range_filter,
    make_stars_filter,
    filter_hotels,
)
from core.calendar import build_price_calendar
from core.domain import Price, Availability, Rule

from tools.db import (
    ensure_calendar_tables,
    fetch_prices_for_calendar,
    fetch_availability_for_calendar,
    fetch_rules_for_rate,
)

# --- Константы UI -------------------------------------------------------------
ROOMTYPE_FIXED = [
    "Стандарт",
    "Стандарт плюс",
    "Стандарт делюкс",
    "VIP стандарт",
    "VIP плюс",
    "VIP делюкс",
]
EXTRAS = ["Завтрак", "Обед", "Ужин", "Бар", "Напитки", "SPA", "Бассейн", "Wi-Fi", "Парковка"]


# --- Утилиты ------------------------------------------------------------------
def load_css(path="assets/app.css"):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
def _parse_list_field(raw) -> list[str]:
    """Принимает CSV/JSON/список/строку и возвращает список строк."""
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
    """Фильтр по наличию имён (нормализованных) в поле списка (roomtype_list/rateplan_list)."""
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
    try:
        css = Path(path).read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass


def _fmt_money(kzt_cents: int | None) -> str:
    if kzt_cents is None:
        return "—"
    return f"{kzt_cents/100:,.0f} ₸".replace(",", " ")


def _iso_cmp(a: str, b: str) -> int:
    # для ISO 'YYYY-MM-DD' сравнение строк == хронологическому
    return (a > b) - (a < b)


def _qp_first(v):
    """Нормализуем значение query param (строка/список/None) -> строка/None."""
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v


def _load_calendar_data(
    hotel_id: int, room_type_id: int, rate_id: int, month_start: date
) -> tuple[tuple[Price, ...], tuple[Availability, ...], tuple[Rule, ...]]:
    ensure_calendar_tables()
    prices = fetch_prices_for_calendar(rate_id, month_start)
    avails = fetch_availability_for_calendar(room_type_id, month_start)
    rules = fetch_rules_for_rate(room_type_id, rate_id)
    return prices, avails, rules


# --- Рендер страницы ----------------------------------------------------------
def render(goto):
    st.title("🔍 Поиск отелей")
    load_css("assets/app.css")

    # rows: id, name, city, price, rating, rooms, available, roomtype, rateplan, owner_id
    rows = fetch_hotels() or []

    # --- Фильтры ---
    st.markdown('<div class="filters-header">⚙️ Фильтры</div>', unsafe_allow_html=True)

    cities = sorted({str(r[2]) for r in rows if r[2]}) if rows else []
    city = st.selectbox("🏙️ Город", ["Все"] + cities)

    max_price_in_data = max((int(r[3]) for r in rows if r[3] is not None), default=100000)
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
            rt_std = st.checkbox("Стандарт", key="rt_std")
            rt_std_plus = st.checkbox("Стандарт плюс", key="rt_std_plus")
        with col2:
            rt_std_delux = st.checkbox("Стандарт делюкс", key="rt_std_delux")
            rt_vip_std = st.checkbox("VIP стандарт", key="rt_vip_std")
        with col3:
            rt_vip_plus = st.checkbox("VIP плюс", key="rt_vip_plus")
            rt_vip_delux = st.checkbox("VIP делюкс", key="rt_vip_delux")
        rt_mode = st.radio("Совпадение типов", ["Любой", "Все"], horizontal=True, key="rt_mode")
        selected_roomtypes = [
            name
            for flag, name in [
                (rt_std, "Стандарт"),
                (rt_std_plus, "Стандарт плюс"),
                (rt_std_delux, "Стандарт делюкс"),
                (rt_vip_std, "VIP стандарт"),
                (rt_vip_plus, "VIP плюс"),
                (rt_vip_delux, "VIP делюкс"),
            ]
            if flag
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

    # --- Подготовка данных для списка ---
    items = []
    for r in rows:
        roomtype_list = _parse_list_field(r[7])  # типы номеров
        rateplan_list = _parse_list_field(r[8])  # доп. услуги
        items.append(
            {
                "id": int(r[0]),
                "name": r[1],
                "city": r[2],
                "price": int(r[3]),
                "rating": float(r[4]),
                "rooms": int(r[5]),
                "available": bool(r[6]),
                "roomtype_list": roomtype_list,
                "rateplan_list": rateplan_list,
            }
        )

    preds = [
        make_city_filter(city),
        make_price_range_filter(0, max_price),
        make_stars_filter(min_stars),
        _make_name_presence_filter(
            "roomtype_list", selected_roomtypes, require_all=(rt_mode == "Все")
        ),
        _make_name_presence_filter(
            "rateplan_list", selected_extras, require_all=(rp_mode == "Все")
        ),
    ]

    filtered = filter_hotels(items, preds)

    if not filtered:
        st.info("Нет отелей по заданным критериям. Попробуйте снять часть фильтров (типы/услуги).")
        return

    # --- Список результатов ---
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

            # Кнопка перехода на бронирование
            if st.button("Забронировать", key=f"book_{h['id']}"):
                if not st.session_state.get("user"):
                    st.error("Сначала войдите в систему.")
                else:
                    st.session_state.selected_hotel_id = h["id"]
                    goto("booking")  # маршрут в нижнем регистре

            # --- Календарь цен для этого отеля ---
            with st.expander("📅 Показать календарь цен", expanded=False):
                # TODO: замените на выбранные room_type_id/rate_id
                room_type_id = 1
                rate_id = 1

                month_start = date.today().replace(day=1)
                prices, avails, rules = _load_calendar_data(h["id"], room_type_id, rate_id, month_start)
                grid = build_price_calendar(room_type_id, rate_id, month_start, prices, avails, rules)

                # ==== namespace для состояния этого конкретного календаря ====
                cal_id = f"h{h['id']}_rt{room_type_id}_rp{rate_id}"
                # берём СНИМОК текущих query params (для построения href)
                qp = dict(st.query_params)
                pick_key = f"pick_{cal_id}"
                cin_key = f"cin_{cal_id}"
                cout_key = f"cout_{cal_id}"

                # Инициализация из URL
                if cin_key not in st.session_state and qp.get(cin_key) is not None:
                    st.session_state[cin_key] = _qp_first(qp.get(cin_key))
                if cout_key not in st.session_state and qp.get(cout_key) is not None:
                    st.session_state[cout_key] = _qp_first(qp.get(cout_key))

                cin = st.session_state.get(cin_key)
                cout = st.session_state.get(cout_key)
                pick = _qp_first(qp.get(pick_key))

                # Клик по дню через query param (?pick_<cal_id>=YYYY-MM-DD)
                if pick:
                    if cin and cout:
                        cin, cout = pick, None
                    elif not cin:
                        cin, cout = pick, None
                    else:
                        if pick == cin:
                            cin, cout = None, None
                        elif _iso_cmp(pick, cin) < 0:
                            cin, cout = pick, None
                        else:
                            cout = pick

                    st.session_state[cin_key], st.session_state[cout_key] = cin, cout

                    # очищаем pick и обновляем cin/cout через st.query_params
                    # (модификация объекта приводит к обновлению URL)
                    if pick_key in st.query_params:
                        del st.query_params[pick_key]
                    if cin:
                        st.query_params[cin_key] = cin
                    else:
                        st.query_params.pop(cin_key, None)
                    if cout:
                        st.query_params[cout_key] = cout
                    else:
                        st.query_params.pop(cout_key, None)

                    st.rerun()

                # Управляющие элементы
                top_l, top_r = st.columns([1, 1])
                with top_l:
                    st.caption("Клик 1 — **заезд**, клик 2 — **выезд**. Повторный клик по заезду — сброс.")
                with top_r:
                    if st.button("Очистить выбор", key=f"clear_{cal_id}", use_container_width=True):
                        st.session_state[cin_key] = None
                        st.session_state[cout_key] = None
                        # удаляем только ключи этого календаря
                        st.query_params.pop(pick_key, None)
                        st.query_params.pop(cin_key, None)
                        st.query_params.pop(cout_key, None)
                        st.rerun()

                # Подготовим карты цен/доступности
                price_by_day, avail_by_day = {}, {}
                for week in grid:
                    for c in week:
                        price_by_day[c.d_iso] = c.amount
                        avail_by_day[c.d_iso] = bool(getattr(c, "available", True))

                # Сводка выбранного диапазона
                if cin and cout and _iso_cmp(cout, cin) > 0:
                    cin_d = date.fromisoformat(cin)
                    cout_d = date.fromisoformat(cout)
                    nights = (cout_d - cin_d).days

                    total = 0
                    ok = True
                    d = cin_d
                    while d < cout_d:
                        d_iso = d.isoformat()
                        if not avail_by_day.get(d_iso, False) or price_by_day.get(d_iso) is None:
                            ok = False
                        total += (price_by_day.get(d_iso) or 0)
                        d = d + timedelta(days=1)

                    msg = (
                        f"**Заезд:** {cin}  ·  **Выезд:** {cout}  ·  "
                        f"**Ночей:** {nights}  ·  **Сумма:** {_fmt_money(total)}"
                    )
                    (st.success if ok else st.warning)(
                        msg + ("" if ok else "  ·  ⚠️ Есть недоступные/пустые дни в диапазоне")
                    )
                    if ok and st.button("✅ Подтвердить даты", key=f"confirm_{cal_id}", type="primary", use_container_width=True):
                        st.session_state[f"selected_range_{cal_id}"] = {
                            "checkin": cin,
                            "checkout": cout,
                            "nights": nights,
                            "total": total,
                        }
                        st.toast(f"Выбрано: {cin} → {cout} ({nights} ноч.)")

                elif cin and not cout:
                    st.info(f"Выберите дату выезда после {cin}")

                # Рендер сетки
                for week in grid:
                    cols = st.columns(7)
                    for i, cell in enumerate(week):
                        day = cell.d_iso[-2:]
                        price_str = _fmt_money(cell.amount)
                        flags = " · ".join(getattr(cell, "flags", []) or [])
                        avail = "✅" if getattr(cell, "available", True) else "❌"

                        disabled = (cell.amount is None) or (not getattr(cell, "available", True))
                        in_range = bool(
                            cin and cout and _iso_cmp(cin, cell.d_iso) < 0 and _iso_cmp(cell.d_iso, cout) < 0
                        )
                        is_edge = (cin and cell.d_iso == cin) or (cout and cell.d_iso == cout)

                        cls = []
                        if disabled:
                            cls.append("muted")
                        if in_range:
                            cls.append("in-range")
                        if is_edge:
                            cls.append("edge")

                        # формируем ссылку с ДОБАВЛЕННЫМ pick, сохраняя остальные параметры
                        href_params = dict(st.query_params)
                        if not disabled:
                            href_params[pick_key] = cell.d_iso
                        href = "?" + urlencode(href_params, doseq=True) if not disabled else "#"

                        html = f"""
                        <div class="cal">
                          <a class="{' '.join(cls)}" href="{href}">
                            <b>{day}</b> {avail}<br><br>{price_str}{('<br><em>'+flags+'</em>') if flags else ''}
                          </a>
                        </div>
                        """
                        cols[i].markdown(html, unsafe_allow_html=True)
