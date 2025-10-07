import streamlit as st
import re
import hashlib
from datetime import datetime, date
from tools.db import init_db, seed_database, fetch_hotels, insert_booking, fetch_user_by_email, get_connection
from core.domain import Hotel, User, Booking
from core.transforms import total_cost_all
from core.recursion import sum_guests, count_bookings
from core.filtres import make_city_filter, make_price_range_filter, filter_hotels


init_db()
seed_database()

st.set_page_config(page_title="Hotel Booking System", page_icon="🏨", layout="wide")

# --- Состояния ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "user" not in st.session_state:
    st.session_state.user = None

# --- Стили верхнего меню ---
st.markdown("""
    <style>
    .top-navbar {
        position: fixed;
        top: 0; left: 0; right: 0;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 10px 25px;
        z-index: 999;
    }
    .top-navbar button {
        border: none;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 6px 15px;
        margin-left: 10px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    .top-navbar button:hover {
        background-color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Верхняя панель ---
st.markdown('<div class="top-navbar">', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns([6, 1.2, 1.2, 1.6, 1.6, 1.8, 1.2])

def set_page(p):
    st.session_state.page = p

with col2:
    if st.button("Регистрация"):
        set_page("register")
with col3:
    if st.button("Вход"):
        set_page("login")
with col4:
    if st.button("Поиск отелей"):
        set_page("search")
with col5:
    if st.button("Мои бронирования"):
        set_page("bookings")
with col6:
    if st.button("Админ панель"):
        set_page("admin")
with col7:
    if st.button("Выйти"):
        st.session_state.user = None
        st.session_state.page = "welcome"
        st.success("Вы вышли из аккаунта.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><br><br>", unsafe_allow_html=True)

# --- Контент страниц ---
page = st.session_state.page

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
# --- Главная ---
if page == "welcome":
    st.title("🏨 Hotel Booking System")
    st.write("Добро пожаловать! Используйте меню сверху.")



# --- Регистрация ---
elif page == "register":
    st.title("📝 Регистрация")
    username = st.text_input("Имя пользователя", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Пароль", type="password", key="reg_pass")
    if st.button("Зарегистрироваться"):
        if not (username and email and password):
            st.error("Заполните все поля.")
        elif not is_valid_email(email):
            st.error("Некорректный email.")
        else:
            with get_connection() as conn:
                cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                                (username, email, hash_password(password)))
                    conn.commit()
                    st.success("Аккаунт создан. Теперь войдите.")
                except Exception as e:
                    st.error(f"Ошибка регистрации: возможно, email уже занят. {e}")

# --- Вход ---
elif page == "login":
    st.title("🔑 Вход")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Пароль", type="password", key="login_pass")
    if st.button("Войти"):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, username, email, password FROM users WHERE email=?", (email,))
            user = cur.fetchone()
            if user and hash_password(password) == user[3]:
                st.session_state.user = {"id": user[0], "username": user[1], "email": user[2]}
                st.success(f"Добро пожаловать, {user[1]}!")
                set_page("search")
            else:
                st.error("Неверные данные.")

# --- Поиск отелей ---
elif page == "search":
    st.title("🔍 Поиск отелей")
    rows = fetch_hotels()
    cities = sorted({r[2] for r in rows}) if rows else []
    city = st.selectbox("Город", ["Все"] + cities)
    max_price = st.slider("Максимальная цена", 0, 100000, 50000)

    preds = []
    if city != "Все":
        preds.append(make_city_filter(city))
    preds.append(make_price_range_filter(0, max_price))
    combined = lambda h: all(p(h) for p in preds)

    hotels_rows = fetch_hotels(city if city != "Все" else None, max_price)
    hotels = [Hotel(id=r[0], name=r[1], city=r[2], price=r[3], rating=r[4], rooms=r[5], available=bool(r[6])) for r in hotels_rows]
    filtered = list(filter(combined, hotels))

    # Track selected hotel for booking
    if "selected_hotel_id" not in st.session_state:
        st.session_state.selected_hotel_id = None

    if filtered:
        for h in filtered:
            st.markdown(f"### {h.name} — {h.city}")
            st.write(f"Цена: {h.price} ₸ | Рейтинг: {h.rating} | Номеров: {h.rooms}")
            if st.button(f"Забронировать {h.name}", key=f"book_{h.id}"):
                if not st.session_state.user:
                    st.error("Сначала войдите в систему.")
                else:
                    st.session_state.selected_hotel_id = h.id

            # Show booking form only for selected hotel
            if st.session_state.selected_hotel_id == h.id and st.session_state.user:
                check_in = st.date_input("Дата заезда", min_value=date.today(), key=f"ci_{h.id}")
                check_out = st.date_input("Дата выезда", min_value=check_in, key=f"co_{h.id}")
                guests = st.number_input("Гостей", 1, 10, key=f"gu_{h.id}")
                if st.button("Подтвердить бронирование", key=f"confirm_{h.id}"):
                    insert_booking(st.session_state.user["id"], h.id, check_in.isoformat(), check_out.isoformat(), guests)
                    st.success("Бронирование успешно создано.")
                    st.session_state.selected_hotel_id = None  # Reset after booking
    else:
        st.info("Нет отелей по заданным критериям.")
# --- Мои бронирования ---
elif page == "bookings":
    st.title("📚 Мои бронирования")
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

# --- Админ панель ---
elif page == "admin":
    st.title("🛠️ Админ панель")
    if not st.session_state.user or st.session_state.user["email"] != "admin@hotel.com":
        st.error("Доступ запрещён.")
    else:
        tab1, tab2, tab3 = st.tabs(["Отели", "Бронирования", "Добавить отель"])

        # Отели
        with tab1:
            st.subheader("Управление отелями")
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, name, city, price, rating, rooms FROM hotels")
                rows = cur.fetchall()
            for r in rows:
                col1, col2 = st.columns([4, 1])
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

        # Бронирования
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
                col1, col2 = st.columns([4, 1])
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

        # Добавление отеля
        with tab3:
            st.subheader("Добавить отель")
            name = st.text_input("Название")
            city = st.text_input("Город")
            price = st.number_input("Цена", min_value=0)
            rating = st.slider("Рейтинг", 0.0, 5.0, 4.0, 0.1)
            rooms = st.number_input("Номеров", min_value=1)
            if st.button("Добавить отель"):
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO hotels (name, city, price, rating, rooms, available)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (name, city, price, rating, rooms))
                    conn.commit()
                st.success("Отель добавлен.")
                st.experimental_rerun()
