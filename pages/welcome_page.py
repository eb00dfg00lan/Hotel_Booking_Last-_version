import streamlit as st
from core.guards import sign_out

def render(goto):
    # Hero
    st.markdown("## 🏨 Добро пожаловать в Hotel Booking System")
    st.markdown(
        "Найдите и забронируйте отель за пару кликов. "
        "Используйте верхнее меню или начните отсюда ↓"
    )

    # Quick actions (adaptive to auth state)
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])
    with c1:
        if st.button("🔍 Начать поиск", use_container_width=True):
            goto("search")

    if st.session_state.get("user"):
        user = st.session_state["user"]
        role = user.get("role", "guest")

        with c2:
            # 🔹 Для гостя — показываем "Мои бронирования"
            if role == "guest":
                if st.button("📚 Мои бронирования", use_container_width=True):
                    goto("bookings")

            # 🔹 Для партнёра — показываем "Мои отели"
            elif role == "partner":
                if st.button("🏨 Мои отели", use_container_width=True):
                    goto("partner_hotels")

            # 🔹 Для админа — панель администратора
            elif role == "admin":
                if st.button("⚙️ Панель администратора", use_container_width=True):
                    goto("admin")

        with c3:
            if st.button("Выйти", key="logout"):
                sign_out()
                st.success("Вы вышли из аккаунта.")
                goto("welcome")

    else:
        with c2:
            if st.button("🔑 Войти", use_container_width=True):
                goto("login")
        with c3:
            if st.button("📝 Регистрация", use_container_width=True):
                goto("register")


    st.divider()

    # Highlights / benefits
    st.markdown("### Почему мы?")
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown("**⚡ Быстро**  \nФильтры по городу, цене и ★ за пару секунд.")
    with b2:
        st.markdown("**💳 Прозрачно**  \nЦена за ночь и итог за всё пребывание.")
    with b3:
        st.markdown("**🔒 Безопасно**  \nРегистрация и вход — в пару кликов.")

    st.caption("Совет: начните с «🔍 Начать поиск», затем выберите отель и оформите бронь на отдельной странице «Booking».")
