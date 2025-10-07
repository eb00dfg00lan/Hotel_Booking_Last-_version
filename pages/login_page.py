import re
import hashlib
import streamlit as st
from tools.db import get_connection

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def render(goto):
    st.title("🔑 Вход")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Пароль", type="password", key="login_pass")
    c1, c2 =st.columns([1,1])
    with c1:
        if st.button("Войти"):
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, username, email, password FROM users WHERE email=?", (email,))
                user = cur.fetchone()
                if user and _hash_password(password) == user[3]:
                    st.session_state.user = {"id": user[0], "username": user[1], "email": user[2]}
                    st.success(f"Добро пожаловать, {user[1]}!")
                    goto("search")
                else:
                    st.error("Неверные данные.")
    with c2:
        if st.button("Ещё нет аккаунта?", key="go_register"):
            goto("register")
