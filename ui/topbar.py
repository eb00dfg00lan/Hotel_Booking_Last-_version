import streamlit as st
from core.guards import sign_out

ALLOWED_ROLES = {"guest", "partner", "admin"}
# где прячем auth-блок справа; добавлены оба варианта регистрации
HIDE_AUTH_ON_PAGES = {"login", "signup", "register", "password_reset"}


def get_current_role() -> str:
    """Безопасно определяем роль: при любом мусоре -> 'guest'."""
    user = st.session_state.get("user") or {}
    role = (user.get("role") or st.session_state.get("role") or "guest").strip().lower()
    return role if role in ALLOWED_ROLES else "guest"


def render_header(goto, page: str | None = None):
    """
    Верхняя панель: слева навигация + (для авторизованных) поповер аккаунта,
    справа — auth-кнопки только для гостя (и только вне HIDE_AUTH_ON_PAGES).
    """
    # Текущая страница
    page = page or st.session_state.get("page") or st.session_state.get("route") or ""
    user = st.session_state.get("user")
    # Правый блок скрываем на спец-страницах и всегда, если пользователь авторизован
    hide_right = (page in HIDE_AUTH_ON_PAGES) or bool(user)

    # --- CSS шапки
    st.markdown(
        """
        <style>
        .__topbar { position: sticky; top: 0; z-index: 999;
            backdrop-filter: blur(6px);
            border-bottom: 1px solid rgba(49,51,63,0.2);
            padding: .25rem 0 .35rem 0;
            background: rgba(255,255,255,0.65);
        }
        [data-theme="dark"] .__topbar { background: rgba(13,17,23,0.65); }
        .__topbar .stButton>button { padding: .35rem .75rem; }
        </style>
        <div class="__topbar"></div>
        """,
        unsafe_allow_html=True,
    )

    # --- Навигация для callback-ов (без st.rerun)
    def goto_cb(p: str):
        st.session_state["page"] = p  # callback -> rerun произойдёт автоматически

    def do_logout_cb():
        # callback: только сайд-эффекты, без st.rerun()
        try:
            sign_out()
        finally:
            st.session_state.pop("user", None)
            st.session_state["role"] = "guest"
            st.session_state["page"] = "welcome"

    # --- Разметка шапки
    top = st.container()
    with top:
        left, right = st.columns([0.7, 0.3], vertical_alignment="center")

        # ЛЕВО: навигация (всегда доступна), плюс поповер аккаунта для авторизованных
        with left:
            role = get_current_role()
            col_a, col_b, col_c = st.columns([0.4, 0.3, 0.3])

            with col_a:
                st.button("🏨 Главная страница", key="nav_welcome",
                          on_click=goto_cb, args=("welcome",))
            with col_b:
                st.button("🔎 Поиск", key="nav_search", type="primary",
                          on_click=goto_cb, args=("search",))

           

        # ПРАВО: показываем ТОЛЬКО для гостя и ТОЛЬКО если страница не из скрытых
        # Заменить весь этот фрагмент
    with right:
        # скрываем весь правый блок на спец-страницах (login/register/...)
        if page in HIDE_AUTH_ON_PAGES:
            return

        user = st.session_state.get("user")
        role = get_current_role()

        if user:
            # АВТОРИЗОВАН: показываем popover аккаунта
            label = f"👤 {user.get('username', 'Гость')}"
            # (если st.popover нет в вашей версии — замените на st.expander(label))
            with st.popover(label, use_container_width=True):
                st.caption(f"Роль: :blue[{role}]")
                st.divider()

                st.button("👤 Профиль", key="profile_btn",
                        on_click=goto_cb, args=("profile",))

                # Роль-зависимые пункты
                if role == "guest":
                    st.button("📜 Мои бронирования", key="my_bookings_btn",
                            on_click=goto_cb, args=("my_bookings",))

                if role == "partner":
                    st.button("🏨 Мои отели", key="my_hotels_btn",
                            on_click=goto_cb, args=("my_hotels",))
                    st.button("📦 Бронирования (партнёр)", key="bookings_partner_btn",
                            on_click=goto_cb, args=("booking_partner",))
                    st.button("➕ Добавить отель", key="add_hotel_btn",
                            on_click=goto_cb, args=("add_hotel",))

                if role == "admin":
                    st.button("🛠️ Админ-панель", key="admin_dash_btn",
                            on_click=goto_cb, args=("admin_dashboard",))

                st.divider()
                st.button("🚪 Выйти", key="logout_btn", on_click=do_logout_cb)

        else:
            # ГОСТЬ: показываем Войти / Регистрация
            c1, c2 = st.columns(2)
            with c1:
                st.button("Войти", key="login_btn",
                        on_click=goto_cb, args=("login",))
            with c2:
                st.button("Регистрация", key="signup_btn",
                        on_click=goto_cb, args=("register",))



