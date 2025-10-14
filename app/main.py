import streamlit as st
from tools.db import init_db, seed_database
from ui import topbar
from pages import (
    booking_page, login_page, register_page, booking_guest_page,booking_partner_page,my_hotels_page,
    admin_page, welcome_page, search_page,add_hotel_page
)
from pathlib import Path
from core.guards import require_roles

# --- utils ---
def load_css(path="assets/app.css"):
    css = Path(path).read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# --- app setup ---
st.set_page_config(page_title="Hotel Booking System", page_icon="🏨", layout="wide")
load_css()
init_db(); seed_database()

# --- session defaults ---
ss = st.session_state
if "page" not in ss: ss.page = "welcome"
if "user" not in ss: ss.user = None           # <-- FIX: было ss.usern
if "selected_hotel_id" not in ss: ss.selected_hotel_id = None
if "role" not in ss: ss.role = "guest"



def goto(p: str):
    ss.page = p
    st.rerun()0


def render_with_topbar(body_fn):
    left, right = st.columns([0.8, 0.2])
    with left:
        topbar.render_header(goto)   
        body_fn(goto)                
    with right:
        topbar.render_auth(goto)    


def partner_guarded(goto):
    require_roles("partner", "admin")
    booking_partner_page.render(goto)

    my_hotels_page.render(goto)


def admin_guarded(goto):
    require_roles("admin")
    admin_page.render(goto)


if ss.page == "login":
    render_with_topbar(login_page.render); st.stop()

if ss.page == "register":
    render_with_topbar(register_page.render); st.stop()

if ss.page == "welcome":
    welcome_page.render(goto); st.stop()

if ss.page == "search":
    render_with_topbar(search_page.render); st.stop()

if ss.page == "booking_guest":
    render_with_topbar(booking_guest_page.render); st.stop()

if ss.page == "booking_partner":
    render_with_topbar(booking_partner_page.render); st.stop()

if ss.page == "my_hotels":
    render_with_topbar(my_hotels_page.render); st.stop()

if ss.page == "Booking":
    render_with_topbar(booking_page.render); st.stop()
if ss.page == "add_hotel":
    render_with_topbar(add_hotel_page.render); st.stop()

role = topbar.get_current_role() or ss.get("role", "guest")

tabs_by_role = {
    "admin": [
        ("Брони",     booking_page.render),
        ("Партнёры",  partner_guarded),
        ("Админ",     admin_guarded),
    ],
    "partner": [
        ("Мои отели", my_hotels_page.render),
        ("Брони",     booking_partner_page.render),
        ("Добавить отель", add_hotel_page.render),
    ],
    "guest": [
        ("Мои брони", booking_guest_page.render),
    ],
}

left, right = st.columns([0.8, 0.2])
with left:
    topbar.render_header(goto)
    labels_fns = tabs_by_role.get(role, tabs_by_role["guest"])
    labels = [name for name, _ in labels_fns]
    fns    = [fn   for _,    fn in labels_fns]
    for tab, render_fn in zip(st.tabs(labels), fns):
        with tab:
            render_fn(goto)

with right:
    topbar.render_auth(goto)
