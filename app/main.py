import streamlit as st
from tools.db import init_db, seed_database
from ui.topbar import render_topbar
from pages import search_page, booking_page, login_page, register_page, bookings_page, admin_page, welcome_page
from pathlib import Path

def load_css(path="assets/app.css"):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ...
st.set_page_config(page_title="Hotel Booking System", page_icon="🏨", layout="wide")
load_css()  # <-- добавить эту строку

# --- init ---
init_db()
seed_database()

# --- session defaults ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"  # <- страница по умолчанию (строка!)
if "user" not in st.session_state:
    st.session_state.user = None
if "selected_hotel_id" not in st.session_state:
    st.session_state.selected_hotel_id = None

def goto(p: str):
    st.session_state.page = p
    st.rerun()

# --- top bar всегда показываем сверху ---

# --- router ---
page_map = {
    "search":   lambda: search_page.render(goto),
    "Booking":  lambda: booking_page.render(goto),
    "login":    lambda: login_page.render(goto),
    "register": lambda: register_page.render(goto),
    "bookings": lambda: bookings_page.render(goto),
    "admin":    lambda: admin_page.render(goto),
    "welcome":  lambda: welcome_page.render(goto),  # опц. пустая домашняя
}

# fallback — если ключ неверный, покажем поиск
page_map.get(st.session_state.page, lambda: search_page.render(goto))()
