import streamlit as st

def render_topbar(goto):
    st.markdown('<div class="top-navbar">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6, c7 = st.columns([6, 1.2, 1.2, 1.6, 1.6, 1.8, 1.2])
    with c2:
        if st.button("Регистрация"): goto("register")
    with c3:
        if st.button("Вход"): goto("login")
    with c4:
        if st.button("Поиск отелей"): goto("search")
    with c5:
        if st.button("Мои бронирования"): goto("bookings")
    with c6:
        if st.button("Админ панель"): goto("admin")
    with c7:
        if st.button("Выйти"):
            st.session_state.user = None
            st.session_state.selected_hotel_id = None
            goto("welcome")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)