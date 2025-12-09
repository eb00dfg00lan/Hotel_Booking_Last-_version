import re
import time
import asyncio
import hashlib
import streamlit as st
from tools.db import get_connection

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _is_valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

class NotificationBus:
    def __init__(self, delay=0.5):
        self.subscribers = {}
        self.delay = delay

    def subscribe(self, event_name, handler):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(handler)

    def emit(self, event_name, data=None):
        time.sleep(self.delay)
        if event_name in self.subscribers:
            for handler in self.subscribers[event_name]:
                handler(data)

bus = NotificationBus(delay=0.5)

def send_notification(msg):
    st.info(msg)

def mul(a, b):
    return a * b

def summ(a, b):
    return a + b

class UserMetricsService:
    def __init__(self, multiply_func, add_func):
        self.multiply = multiply_func
        self.add = add_func

    def compute_metric(self, name_len, email_score):
        return self.add(self.multiply(name_len, email_score), name_len)

def user_metrics_factory():
    return UserMetricsService(mul, summ)

def handle_user_registration_metrics(user_data):
    username = user_data["name"]
    email = user_data["email"]
    email_score = email.count("@") + len(username)
    service = user_metrics_factory()
    metric = service.compute_metric(len(username), email_score)
    send_notification(f"{username} успешно зарегистрирован! Email Score:{email_score} | Метрика:{metric}")

async def fetch_data(i):
    await asyncio.sleep(0.1)
    return f"data_{i}"

async def transform_data(data):
    await asyncio.sleep(0.1)
    return data.upper()

async def run_data_pipeline(username):
    raw = await asyncio.gather(*(fetch_data(i) for i in range(3)))
    processed = await asyncio.gather(*(transform_data(d) for d in raw))
    send_notification(f"{username} Pipeline завершён: {processed}")

def handle_user_registration_pipeline(user_data):
    username = user_data["name"]
    asyncio.create_task(run_data_pipeline(username))

bus.subscribe("user_registered", handle_user_registration_metrics)
bus.subscribe("user_registered", handle_user_registration_pipeline)

def register_user(name, email):
    bus.emit("user_registered", {"name": name, "email": email})



def render(goto):
    st.title("📝 Регистрация")
    username = st.text_input("Имя пользователя", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Пароль", type="password", key="reg_pass") 
    
    role_map = {"guest": "Гость", "partner": "Партнёр"}
    role = st.radio(
        "Роль",
        options=["guest", "partner"],
        index=0,
        horizontal=True,
        format_func=lambda x: role_map[x],
        key="reg_role",
    )
    
    col_submit, col_login = st.columns([1,1])
    with col_submit:
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
                            "INSERT INTO users (username, email, password,role) VALUES (?, ?, ?, ?)",
                            (username, email, _hash_password(password),role),
                        )
                        conn.commit()
                        st.success("Аккаунт создан. Теперь войдите.")
                        goto("login")
                    except Exception as e:
                        st.error(f"Ошибка регистрации: возможно, email уже занят. {e}")
    with col_login:
        if st.button("Уже есть аккаунт", key="go_register"):
            goto("login")