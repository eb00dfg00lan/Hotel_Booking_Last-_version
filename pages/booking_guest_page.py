import streamlit as st
from tools.db import get_connection

def render(goto):
    st.title("📚 Мои бронирования")

    user = st.session_state.get("user")
    if not user:
        st.error("Войдите, чтобы увидеть свои брони.")
        return

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, h.name, h.city, b.check_in, b.check_out, b.guests, h.price, h.rating
            FROM bookings b
            JOIN hotels h ON b.hotel_id = h.id
            WHERE b.user_id = ?
            ORDER BY b.id DESC
        """, (user["id"],))
        rows = cur.fetchall()

    if not rows:
        st.info("У вас нет бронирований.")
        return

    st.markdown(f"**Всего бронирований:** {len(rows)}")
    st.divider()

    # --- вывод в экспандерах ---
    for (bid, name, city, check_in, check_out, guests, price, rating) in rows:
        with st.expander(f"🆔 {bid} | 🏨 {name} ({city})", expanded=False):
            st.write(f"📅 **Даты:** {check_in} → {check_out}")
            st.write(f"👥 **Гостей:** {guests}")
            st.write(f"💵 **Цена за ночь:** {int(price)} ₸")
            st.write(f"⭐ **Рейтинг:** {rating:.1f}")
