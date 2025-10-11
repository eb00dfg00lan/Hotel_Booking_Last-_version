# core/guards.py
import streamlit as st
from typing import Iterable

def current_user():
    return st.session_state.get("user")

def current_role() -> str:
    u = current_user()
    return (u.get("role") if isinstance(u, dict) else getattr(u, "role", None)) or "guest"

def has_role(*roles: Iterable[str]) -> bool:
    return current_role() in roles

def require_roles(*roles: str):
    if not has_role(*roles):
        st.error("🚫 Доступ запрещён.")
        st.stop()

def sign_out():
    st.session_state.pop("user", None)
    st.session_state.pop("role", None)
