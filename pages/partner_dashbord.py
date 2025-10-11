import streamlit as st
from tools.db import get_connection

def render(goto):
    tab1, tab2, tab3 = st.tabs(["Отели", "Бронирования", "Добавить отель"])

    with tab1:
        st.subheader("Управление отелями")
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, city, price, rating, rooms FROM hotels ORDER BY id DESC")
            rows = cur.fetchall()
        for r in rows:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"🏨 {r[1]} | {r[2]} | {r[3]} ₸ | ⭐ {r[4]} | 🛏 {r[5]}")
            with col2:
                if st.button("Удалить", key=f"del_h_{r[0]}"):
                    with get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM hotels WHERE id=?", (r[0],))
                        conn.commit()
                    st.success("Отель удалён.")
                    st.rerun()

    with tab2:
        st.subheader("Все бронирования")
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT b.id, u.username, h.name, b.check_in, b.check_out, b.guests
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                JOIN hotels h ON b.hotel_id = h.id
                ORDER BY b.id DESC
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
                    st.rerun()

    with tab3:
        st.subheader("Добавить отель")
        name = st.text_input("Название")
        city = st.text_input("Город")
        price = st.number_input("Цена", min_value=0)
        rating = st.slider("Рейтинг", 0.0, 5.0, 4.0, 0.1)
        rooms = st.number_input("Номеров", min_value=1, step=1)
        if st.button("Добавить отель"):
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO hotels (name, city, price, rating, rooms, available)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (name, city, price, float(rating), int(rooms)))
                conn.commit()
            st.success("Отель добавлен.")
            st.rerun()