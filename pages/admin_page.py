import streamlit as st
from core.guards import require_roles

def render(goto):
    require_roles("admin")
    st.title("⚙️ Admin Panel")
    st.write("- Пользователи: создание/бан/смена роли")
    st.write("- Все отели: редактирование/удаление")
    st.write("- Все брони: аудит/отмена")
    # Здесь твои таблицы и действия администратора
