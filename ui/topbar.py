import streamlit as st
from core.guards import sign_out

def get_current_role() -> str:
    user = st.session_state.get("user")
    if user and "role" in user:
        return user["role"]
    return st.session_state.get("role", "guest")

def render_auth(goto):
    """Правая часть – всегда показываем."""
    right = st.container()
    with right:
        if st.button("Поиск", key="search"):
            goto("search")
        user = st.session_state.get("user")
        if user:
            username = user.get("username", "Гость")
            role = user.get("role", "guest")
            st.caption(f"👤 {username} ({role})")
            if st.button("Выйти", key="logout"):
                sign_out()
                st.success("Вы вышли из аккаунта.")
                goto("welcome")

def render_header(goto):
    # --- Заголовок, кликабельный ---
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        if st.button("Главная страница", use_container_width=False):
            goto("welcome")   # переход на главную
    return col1, col2
