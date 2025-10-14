import streamlit as st
from core.guards import sign_out



def render(goto):
    # Hero
    st.markdown("""<div class="bg-container">
                <div class="box1"></div>
                <div class="image"></div>
                <div class="box2"></div>
                </div>""", unsafe_allow_html=True)



    st.markdown("""<div class="main-title"> booking.GO</div>""", unsafe_allow_html=True)

    # Quick actions (adaptive to auth state)
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])
    with c1:
        if st.button("Начать поиск", use_container_width=True, key="start_search"):
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
            if st.button("Log in", key="login"):
                goto("login")
        with c3:
            if st.button("Sign up", key="signup"):
                goto("register")

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
