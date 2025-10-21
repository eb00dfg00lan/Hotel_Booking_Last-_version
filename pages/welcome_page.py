import streamlit as st
from core.guards import sign_out

def render(goto):
    # Фон и базовые стили
    st.markdown("""
    <style>
    /* Основной контейнер Streamlit */
    html, body, [class*="stApp"] {
        background-color: black !important; /* чёрный фон */
        color: white;
        position: relative;
        z-index: 0; /* нейтральный уровень — не перекрывает кнопки */
    }

    /* Отдельный фоновый слой — без отрицательного z-index */
    .bg-layer {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: black;
        z-index: 0; /* просто на заднем плане, но не отрицательно */
    }
    </style>

    <div class="bg-layer"></div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="border: none; height: 2px; width: 100%; background-color: rgb(255, 0, 85); top: 67px; right: 0; position: fixed; z-index: 1;"></div>
""", unsafe_allow_html=True)
    st.markdown("""
    <div style="border: none; height: 54%; width: 2px; background-color: rgb(255, 0, 85); top: 67px; right: 20px; position: fixed; z-index: 1;"></div>
""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="border: none; height: 2px; width: 36%; background-color: rgb(255, 0, 85); top: 150px; right: 0; position: fixed; z-index: 1;"></div>
""", unsafe_allow_html=True)
    st.markdown("""
    <div style="border: none; height: 2px; width: 100%; background-color: rgb(255, 0, 85); top: 60.5%; right: 0; position: fixed; z-index: 1;"></div>
""", unsafe_allow_html=True)
    st.markdown("""
    <div style="border: none; height: 100%; width: 2px; background-color: rgb(255, 0, 85); top: 67px; right: 36%; position: fixed; z-index: 1;"></div>
""", unsafe_allow_html=True)


    
    # Дополнительный HTML для твоих блоков
    st.markdown("""
    <div class="bg-container">
        <div class="box1"></div>
        <div class="image"></div>
        <div class="box2"></div>
    </div>
    """, unsafe_allow_html=True)

    # Текстовые элементы
    st.markdown("""<div class="main-title"> booking x GO</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="main-1"> GO</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="main-2"> GO</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="main-3"> GO</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="main-4"> GO</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="main-aboutus"> about us</div>""", unsafe_allow_html=True)

    st.markdown("""
<style>
.about-box {
    width: 600px;
    height: 400px;
    position: fixed;
    top: 170px;
    right: 20px;
    font-weight: bold;
    background-color: rgba(0, 0, 0);
    color: rgb(255, 0, 85);
    position: fixed;
    font-size: 30px;
    padding: 15px;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: flex-start; /* по горизонтали — влево */
    align-items: flex-start;     /* по вертикали — вверх */
    text-align: right; 
    margin: 0;
}
</style>

<div class="about-box">
  <p>
  We are a passionate team dedicated to making travel easier, faster, and more enjoyable.
  Our mission is to connect people with the best booking experiences,
  using technology that feels simple and human. <br><br>
  At <b>Booking x GO</b>, we believe every journey starts with one click —
  and we make sure that click is worth it.
  </p>
</div>
""", unsafe_allow_html=True)
    # Колонки с кнопками
    c1, c2, c3 = st.columns([1.2, 1.2, 1.2])

    with c1:
        if st.button("**search**", use_container_width=True, key="start_search"):
            goto("search")

    if st.session_state.get("user"):
        user = st.session_state["user"]
        role = user.get("role", "guest")

        with c2:
            if role == "guest":
                if st.button("My Bookings", use_container_width=True):
                    goto("bookings")
            elif role == "partner":
                if st.button("My Hotels", use_container_width=True):
                    goto("partner_hotels")
            elif role == "admin":
                if st.button("⚙️ Admin Panel", use_container_width=True):
                    goto("admin")

        with c3:
            if st.button("Log Out", key="logout"):
                sign_out()
                st.success("You have been logged out.")
                goto("welcome")

    else:
        with c2:
            if st.button("**Log in**", key="login"):
                goto("login")
        with c3:
            if st.button("**Sign up**", key="signup"):
                goto("register")
