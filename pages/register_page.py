import re
import hashlib
import streamlit as st
from tools.db import get_connection

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _is_valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def render(goto):
    st.title("📝 Регистрация")
    username = st.text_input("Имя пользователя", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Пароль", type="password", key="reg_pass")
    c1,c2 = st.columns([1,1])
    with c1:
        if st.button("Зарегистрироваться"):
            if not (username and email and password):
                st.error("Заполните все поля.")
            elif not _is_valid_email(email):
                st.error("Некорректный email.")
            else:
                with get_connection() as conn:
                    cur = conn.cursor()
                    try:
                        cur.execute(
                            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                            (username, email, _hash_password(password))
                        )
                        conn.commit()
                        st.success("Аккаунт создан. Теперь войдите.")
                        goto("login")
                    except Exception as e:
                        st.error(f"Ошибка регистрации: возможно, email уже занят. {e}")
    with c2:
        if st.button("Уже есть аккаунт", key="go_register"):
            goto("login")