import streamlit as st
from core.guards import sign_out

def render(goto):

    # Простая версия welcome — без inline-стилей и классов
    st.title("booking x GO")

    # Большой заголовок (как простой markdown, без классов)
    st.markdown("## GO")
    st.markdown("## GO")
    st.markdown("## GO")
    st.markdown("## GO")

    # Описание (заменил about-box на простой markdown)
    st.markdown("""
**About us**

We are a passionate team dedicated to making travel easier, faster, and more enjoyable.
Our mission is to connect people with the best booking experiences,
using technology that feels simple and human.

At **Booking x GO**, we believe every journey starts with one click — and we make sure that click is worth it.
""")

    # Кнопки (оставил логику как была)
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])

    with c1:
        if st.button("**search**", use_container_width=True, key="start_search"):
            goto("search")

    if st.session_state.get("user"):
        user = st.session_state["user"]
        role = user.get("role", "guest")

        with c2:
            if role == "guest":
                if st.button("My Bookings", use_container_width=True):
                    goto("bookings")
            elif role == "partner":
                if st.button("My Hotels", use_container_width=True):
                    goto("partner_hotels")
            elif role == "admin":
                if st.button("⚙️ Admin Panel", use_container_width=True):
                    goto("admin")

        with c3:
            if st.button("Log Out", key="logout"):
                sign_out()
                st.success("You have been logged out.")
                goto("welcome")

    else:
        with c2:
            if st.button("**Log in**", key="login"):
                goto("login")
        with c3:
            if st.button("**Sign up**", key="signup"):
                goto("register")
