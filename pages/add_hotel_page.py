# pages/add_hotel_page.py
import streamlit as st
from tools.db import insert_hotel

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
            name = st.text_input("Название отеля*", key="hotel_name")
            city = st.text_input("Город*", key="hotel_city")

            col1, col2, col3 = st.columns(3)
            with col1:
                price = st.number_input("Цена (за ночь)", min_value=0.0, step=100.0, format="%.2f", key="hotel_price")
            with col2:
                rating = st.number_input("Рейтинг", min_value=0.0, max_value=5.0, step=0.1, format="%.1f", key="hotel_rating")
            with col3:
                rooms = st.number_input("Всего комнат", min_value=0, step=1, key="hotel_rooms")

            col4, col5 = st.columns(2)
            with col4:
                available = st.number_input("Доступно сейчас", min_value=0, step=1, key="hotel_available")
            with col5:
                st.caption("Доступно ≤ Всего комнат (проверяется)")

            roomtype = st.text_input("Типы комнат (через запятую)", placeholder="Standard, Deluxe, Suite", key="hotel_roomtype")
            rateplan = st.text_input("Тарифные планы (через запятую)", placeholder="RO, BB, HB, AI", key="hotel_rateplan")

            submit = st.form_submit_button("Сохранить", use_container_width=True)

        # обработка сабмита
        if submit:
            # простые валидации
            errors = []
            if not name.strip():
                errors.append("Укажите название отеля.")
            if not city.strip():
                errors.append("Укажите город.")
            if rooms < 0:
                errors.append("Число комнат не может быть отрицательным.")
            if available < 0:
                errors.append("Доступно не может быть отрицательным.")
            if available > rooms:
                errors.append("Доступно не может превышать число комнат.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                new_id = insert_hotel(
                    owner_id=owner_id,
                    name=name.strip(),
                    city=city.strip(),
                    price=float(price or 0),
                    rating=float(rating or 0),
                    rooms=int(rooms or 0),
                    available=int(available or 0),
                    roomtype=roomtype,   # строка "a, b, c" — функция сама приведёт
                    rateplan=rateplan,
                )
                if new_id:
                    st.success(f"Отель добавлен (id={new_id}).")
                    # опционально: отправим на страницу с объектами
                    if st.button("Перейти к моим объектам", key="go_my_hotels_btn", use_container_width=True):
                        goto("partner_hotels")
                else:
                    st.error("Не удалось сохранить. Проверьте данные.")
