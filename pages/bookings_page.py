import streamlit as st
from tools.db import get_connection

def render(goto):
    st.title("📚 Мои бронирования")
    if not st.session_state.get("user"):
        st.error("Войдите, чтобы увидеть свои брони.")
        return

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, h.name, b.check_in, b.check_out, b.guests
            FROM bookings b
            JOIN hotels h ON b.hotel_id = h.id
            WHERE b.user_id = ?
            ORDER BY b.id DESC
        """, (st.session_state["user"]["id"],))
        rows = cur.fetchall()

    if rows:
        for r in rows:
            st.write(f"🆔{r[0]} | 🏨 {r[1]} | {r[2]} → {r[3]} | 👥 {r[4]}")
    else:
        st.info("У вас нет бронирований.")
