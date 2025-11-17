import streamlit as st
from pathlib import Path
from core.guards import sign_out

def load_css(path: str) -> None:
    try:
        css = Path(path).read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"CSS not loaded: {e}")

def render(goto):
    
    load_css("assets/app.css")

    # Описание (обёрнут в div с классом about-box)
    st.markdown(
        """
        <div class="about-box">
            <h2>About us</h2>
            <p>
                We are a passionate team dedicated to making travel easier, faster, and more enjoyable.
                Our mission is to connect people with the best booking experiences,
                using technology that feels simple and human.
            </p>
            <p style="margin-top:8px; color: rgba(255,255,255,0.5); font-size:13px;">
                At <strong>Booking x GO</strong>, we believe every journey starts with one click — and we make sure that click is worth it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Кнопки (с тем же поведением)
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])

    with c1:
        # ключ уже был key="start_search" — в CSS я использовал селектор по ключу для выделения
        if st.button("**search**", use_container_width=True, key="start_search"):
            goto("search")

    if st.session_state.get("user"):
        user = st.session_state["user"]
        role = user.get("role", "guest")

        with c2:
            if role == "guest":
                if st.button("My Bookings", use_container_width=True, key="my_bookings"):
                    goto("bookings")
            elif role == "partner":
                if st.button("My Hotels", use_container_width=True, key="my_hotels"):
                    goto("partner_hotels")
            elif role == "admin":
                if st.button("⚙️ Admin Panel", use_container_width=True, key="admin_panel"):
                    goto("admin")

        with c3:
            if st.button("Log Out", key="logout", use_container_width=True):
                sign_out()
                st.success("You have been logged out.")
                goto("welcome")

    else:
        with c2:
            if st.button("**Log in**", key="login", use_container_width=True):
                goto("login")
        with c3:
            if st.button("**Sign up**", key="signup", use_container_width=True):
                goto("register")
