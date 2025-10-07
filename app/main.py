import streamlit as st
from tools.db import init_db, seed_database
from ui.topbar import render_topbar
from pages import search_page, booking_page, login_page, register_page, bookings_page, admin_page

# --- init ---
init_db()
seed_database()
st.set_page_config(page_title="Hotel Booking System", page_icon="🏨", layout="wide")

# --- session defaults ---
if "page" not in st.session_state: st.session_state.page = "welcome"
if "user" not in st.session_state: st.session_state.user = None
if "selected_hotel_id" not in st.session_state: st.session_state.selected_hotel_id = None

def goto(p: str):
    st.session_state.page = p
    st.rerun()

# --- top bar ---
render_topbar(goto)

# --- simple welcome page ---
def page_welcome():
    st.title("🏨 Hotel Booking System")
    st.write("Добро пожаловать! Используйте меню сверху.")

# --- router ---
page_map = {
    "welcome": page_welcome,
    "search":  lambda: search_page.render(goto),
    "Booking": lambda: booking_page.render(goto),
    "login":   lambda: login_page.render(goto),
    "register":lambda: register_page.render(goto),
    "bookings":lambda: bookings_page.render(goto),
    "admin":   lambda: admin_page.render(goto),
}
page_map.get(st.session_state.page, page_welcome)()
