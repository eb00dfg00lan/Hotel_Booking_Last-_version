# pages/add_hotel_page.py
import json
import streamlit as st
from tools.db import insert_hotel


def _amenity_input(label: str, key_prefix: str, step: float = 500.0, default: bool = False) -> dict:
    """
    Чекбокс + число. Поле цены всегда активно.
    Если чекбокс не отмечен — возвращаем price=0.0.
    """
    col_cb, col_price = st.columns([2, 1])
    with col_cb:
        checked = st.checkbox(label, value=default, key=f"{key_prefix}_has")
    with col_price:
        price = st.number_input(
            "Цена",
            min_value=0.0,
            step=max(step, 0.01),
            format="%.2f",
            key=f"{key_prefix}_price",
        )
    return {"has": bool(checked), "price": (float(price) if checked else 0.0)}


def render(goto):
    st.title("➕ Добавить отель")

    user = st.session_state.get("user")
    if not user:
        st.error("Войдите в систему.")
        return
    if user.get("role") not in ("partner", "admin"):
        st.error("Доступ только для партнёров.")
        return

    owner_id = user["id"]

    with st.expander("Форма добавления", expanded=True):
        with st.form("add_hotel_form", clear_on_submit=False):
            # Базовая информация
            name = st.text_input("Название отеля*", key="hotel_name")
            city = st.text_input("Город*", key="hotel_city")

            col1, col2, col3 = st.columns(3)
            with col1:
                price = st.number_input(
                    "Цена (за ночь)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key="hotel_price",
                )
            with col2:
                rating = st.number_input(
                    "Рейтинг",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    format="%.1f",
                    key="hotel_rating",
                )
            with col3:
                rooms = st.number_input("Всего комнат", min_value=0, step=1, key="hotel_rooms")

            col4, col5 = st.columns(2)
            with col4:
                available = st.number_input("Доступно сейчас", min_value=0, step=1, key="hotel_available")
            with col5:
                st.caption("Должно быть: Доступно ≤ Всего комнат")

            # Типы номеров
            with st.expander("Типы номеров", expanded=True):
                # Количества
                c1, c2, c3 = st.columns(3)
                with c1:
                    standart = st.number_input("Стандарт (шт.)", min_value=0, step=1, key="hotel_roomtype_standart")
                with c2:
                    standart_plus = st.number_input("Стандарт плюс (шт.)", min_value=0, step=1, key="hotel_roomtype_standart_plus")
                with c3:
                    standart_deluxe = st.number_input("Стандарт делюкс (шт.)", min_value=0, step=1, key="hotel_roomtype_standart_deluxe")

                # Цены
                p1, p2, p3 = st.columns(3)
                with p1:
                    standart_price = st.number_input("Цена «Стандарт»", min_value=0.0, step=1000.0, format="%.2f", key="hotel_roomtype_standart_price")
                with p2:
                    standart_plus_price = st.number_input("Цена «Стандарт плюс»", min_value=0.0, step=1000.0, format="%.2f", key="hotel_roomtype_standart_plus_price")
                with p3:
                    standart_deluxe_price = st.number_input("Цена «Стандарт делюкс»", min_value=0.0, step=1000.0, format="%.2f", key="hotel_roomtype_standart_deluxe_price")

                st.divider()

                # VIP количества
                vc1, vc2, vc3 = st.columns(3)
                with vc1:
                    vip_standart = st.number_input("VIP стандарт (шт.)", min_value=0, step=1, key="hotel_roomtype_vip_standart")
                with vc2:
                    vip_plus = st.number_input("VIP плюс (шт.)", min_value=0, step=1, key="hotel_roomtype_vip_plus")
                with vc3:
                    vip_deluxe = st.number_input("VIP делюкс (шт.)", min_value=0, step=1, key="hotel_roomtype_vip_deluxe")

                # VIP цены
                vp1, vp2, vp3 = st.columns(3)
                with vp1:
                    vip_standart_price = st.number_input("Цена «VIP стандарт»", min_value=0.0, step=1000.0, format="%.2f", key="hotel_roomtype_vip_standart_price")
                with vp2:
                    vip_plus_price = st.number_input("Цена «VIP плюс»", min_value=0.0, step=1000.0, format="%.2f", key="hotel_roomtype_vip_plus_price")
                with vp3:
                    vip_deluxe_price = st.number_input("Цена «VIP делюкс»", min_value=0.0, step=1000.0, format="%.2f", key="hotel_roomtype_vip_deluxe_price")

            # Доп. услуги — теперь это rateplan (JSON)
            with st.expander("Дополнительные услуги", expanded=True):
                st.markdown("**Питание и сервисы**")
                rp_breakfast = _amenity_input("Завтрак (Breakfast)", "rp_breakfast")
                rp_lunch     = _amenity_input("Обед (Lunch)", "rp_lunch")
                rp_dinner    = _amenity_input("Ужин (Dinner)", "rp_dinner")

                rp_bar       = _amenity_input("Бар", "rp_bar", step=500.0)
                rp_drinks    = _amenity_input("Напитки (Drinks)", "rp_drinks")

                rp_spa       = _amenity_input("SPA", "rp_spa")
                rp_pool      = _amenity_input("Бассейн (Pool)", "rp_pool", step=500.0)

                st.markdown("**Инфраструктура**")
                rp_wifi     = {"has": bool(st.checkbox("Wi-Fi", key="rp_wifi_has", value=True)),  "price": 0.0}
                rp_parking  = {"has": bool(st.checkbox("Парковка", key="rp_parking_has", value=False)), "price": 0.0}

                # Один объект, который положим в колонку rateplan (JSON)
                rateplan_obj = {
                    "breakfast": rp_breakfast,
                    "lunch":     rp_lunch,
                    "dinner":    rp_dinner,
                    "bar":       rp_bar,
                    "drinks":    rp_drinks,
                    "spa":       rp_spa,
                    "pool":      rp_pool,
                    "wifi":      rp_wifi,
                    "parking":   rp_parking,
                }

            submit = st.form_submit_button("Сохранить", use_container_width=True)

        # === Обработка сабмита ===
        if submit:
            errors = []
            if not name.strip():
                errors.append("Укажите название отеля.")
            if not city.strip():
                errors.append("Укажите город.")
            if available > rooms:
                errors.append("Доступно не может превышать число комнат.")

            total_by_types = (
                int(standart)
                + int(standart_plus)
                + int(standart_deluxe)
                + int(vip_standart)
                + int(vip_plus)
                + int(vip_deluxe)
            )
            if total_by_types > int(rooms):
                errors.append(f"Сумма по типам ({total_by_types}) больше, чем всего комнат ({rooms}).")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Сборка JSON по типам номеров
                roomtype_obj = {
                    "Стандарт": {"count": int(standart), "price": float(standart_price)},
                    "Стандарт плюс": {"count": int(standart_plus), "price": float(standart_plus_price)},
                    "Стандарт делюкс": {"count": int(standart_deluxe), "price": float(standart_deluxe_price)},
                    "VIP стандарт": {"count": int(vip_standart), "price": float(vip_standart_price)},
                    "VIP плюс": {"count": int(vip_plus), "price": float(vip_plus_price)},
                    "VIP делюкс": {"count": int(vip_deluxe), "price": float(vip_deluxe_price)},
                }

                new_id = insert_hotel(
                    owner_id=owner_id,
                    name=name.strip(),
                    city=city.strip(),
                    price=float(price or 0.0),
                    rating=float(rating or 0.0),
                    rooms=int(rooms or 0),
                    available=int(available or 0),
                    roomtype=json.dumps(roomtype_obj, ensure_ascii=False),   # JSON по типам
                    rateplan=json.dumps(rateplan_obj, ensure_ascii=False),   # JSON по доп. услугам (бывш. amenities)
                )

                if new_id:
                    st.success(f"Отель добавлен (ID={new_id}).")
                    if st.button("Перейти к моим объектам", key="go_my_hotels_btn", use_container_width=True):
                        goto("my_hotels")
                else:
                    st.error("Не удалось сохранить. Проверьте данные.")
