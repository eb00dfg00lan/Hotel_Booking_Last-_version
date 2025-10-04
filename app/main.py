import streamlit as st
from datetime import datetime, date
from tools.db import init_db, seed_database, fetch_hotels, insert_booking, fetch_user_by_email, get_connection
from core.domain import Hotel, User, Booking
from core.transforms import total_cost_all
from core.recursion import sum_guests, count_bookings
from core.filtres import make_city_filter, make_price_range_filter, filter_hotels


init_db()
seed_database()

st.set_page_config(page_title="Hotel Booking System", page_icon="🏨", layout="centered")
st.title("🏨 Hotel Booking System")

if "user" not in st.session_state:
    st.session_state.user = None

menu = st.sidebar.radio("Меню", ["Главная", "Регистрация", "Вход", "Отели", "Мои бронирования", "Админ панель", "Выход"])


if menu == "Регистрация":
    st.header("Регистрация")
    username = st.text_input("Имя пользователя", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Пароль", type="password", key="reg_pass")
    if st.button("Зарегистрироваться"):
        if username and email and password:
            with get_connection() as conn:
                cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                                (username, email, password))
                    conn.commit()
                    st.success("Аккаунт создан, можете войти.")
                except Exception as e:
                    st.error("Ошибка регистрации: возможно email уже занят.")
        else:
            st.error("Заполните все поля.")


elif menu == "Вход":
    st.header("Вход")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Пароль", type="password", key="login_pass")
    if st.button("Войти"):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, username, email FROM users WHERE email=? AND password=?", (email, password))
            user = cur.fetchone()
            if user:
                st.session_state.user = {"id": user[0], "username": user[1], "email": user[2]}
                st.success(f"Добро пожаловать, {user[1]}!")
            else:
                st.error("Неверные учетные данные.")


elif menu == "Главная":
    st.header("Добро пожаловать")
    st.write("Система бронирования отелей. Используй меню слева.")


elif menu == "Отели":
    st.header("Поиск отелей")


    rows = fetch_hotels()
    cities = sorted({r[2] for r in rows}) if rows else []
    city = st.selectbox("Город", ["Все"] + cities)
    max_price = st.slider("Максимальная цена", 0, 100000, 50000)


    preds = []
    if city != "Все":
        preds.append(make_city_filter(city))
    preds.append(make_price_range_filter(0, max_price))
    combined = (lambda h: all(p(h) for p in preds))


    hotels_rows = fetch_hotels(city if city != "Все" else None, max_price)
    hotels = [Hotel(id=r[0], name=r[1], city=r[2], price=r[3], rating=r[4], rooms=r[5], available=bool(r[6])) for r in hotels_rows]
    filtered = list(filter(combined, hotels))
    if filtered:
        for h in filtered:
            st.markdown(f"### {h.name} — {h.city}")
            st.write(f"Цена: {h.price} ₸ | Рейтинг: {h.rating} | Номеров: {h.rooms}")
            if st.button(f"Забронировать {h.name}", key=f"book_{h.id}"):
                if not st.session_state.user:
                    st.error("Сначала войдите в систему.")
                else:
                    check_in = st.date_input("Дата заезда", min_value=date.today(), key=f"ci_{h.id}")
                    check_out = st.date_input("Дата выезда", min_value=check_in, key=f"co_{h.id}")
                    guests = st.number_input("Гостей", 1, 10, key=f"gu_{h.id}")
                    if st.button("Подтвердить бронирование", key=f"confirm_{h.id}"):
                        insert_booking(st.session_state.user["id"], h.id, check_in.isoformat(), check_out.isoformat(), guests)
                        st.success("Бронирование успешно создано.")
    else:
        st.info("Нет отелей по заданным критериям.")

elif menu == "Мои бронирования":
    st.header("Мои бронирования")
    if not st.session_state.user:
        st.error("Войдите, чтобы увидеть свои брони.")
    else:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT b.id, h.name, b.check_in, b.check_out, b.guests
                FROM bookings b JOIN hotels h ON b.hotel_id = h.id
                WHERE b.user_id = ?
            """, (st.session_state.user["id"],))
            rows = cur.fetchall()
        if rows:
            for r in rows:
                st.write(f"🆔{r[0]} | 🏨 {r[1]} | {r[2]} → {r[3]} | 👥 {r[4]}")
        else:
            st.info("У вас нет бронирований.")

elif menu == "Админ панель":
    st.header("Админ панель")
    if not st.session_state.user or st.session_state.user["email"] != "admin@hotel.com":
        st.error("Доступ запрещён.")
    else:
        tab1, tab2, tab3 = st.tabs(["Отели", "Бронирования", "Добавить отель"])
        with tab1:
            st.subheader("Управление отелями")
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, name, city, price, rating, rooms, available FROM hotels")
                rows = cur.fetchall()
            for r in rows:
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"🏨 {r[1]} | {r[2]} | {r[3]} ₸ | ⭐ {r[4]}")
                with col2:
                    if st.button("Удалить", key=f"del_h_{r[0]}"):
                        with get_connection() as conn:
                            cur = conn.cursor()
                            cur.execute("DELETE FROM hotels WHERE id=?", (r[0],))
                            conn.commit()
                        st.success("Отель удалён.")
                        st.experimental_rerun()
        with tab2:
            st.subheader("Все бронирования")
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT b.id, u.username, h.name, b.check_in, b.check_out, b.guests
                    FROM bookings b
                    JOIN users u ON b.user_id = u.id
                    JOIN hotels h ON b.hotel_id = h.id
                """)
                rows = cur.fetchall()
            for r in rows:
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"🆔{r[0]} | 👤{r[1]} | 🏨{r[2]} | {r[3]} → {r[4]} | 👥 {r[5]}")
                with col2:
                    if st.button("Удалить", key=f"del_b_{r[0]}"):
                        with get_connection() as conn:
                            cur = conn.cursor()
                            cur.execute("DELETE FROM bookings WHERE id=?", (r[0],))
                            conn.commit()
                        st.success("Бронирование удалено.")
                        st.experimental_rerun()
        with tab3:
            st.subheader("Добавить отель")
            name = st.text_input("Название", key="new_name")
            city = st.text_input("Город", key="new_city")
            price = st.number_input("Цена", min_value=0, key="new_price")
            rating = st.slider("Рейтинг", 0.0, 5.0, 4.0, 0.1, key="new_rating")
            rooms = st.number_input("Номеров", min_value=1, key="new_rooms")
            if st.button("Добавить отель", key="add_h"):
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO hotels (name, city, price, rating, rooms, available) VALUES (?, ?, ?, ?, ?, ?)",
                                (name, city, price, rating, rooms, 1))
                    conn.commit()
                st.success("Отель добавлен.")
                st.experimental_rerun()

elif menu == "Выход":
    st.session_state.user = None
    st.success("Вы вышли.")
