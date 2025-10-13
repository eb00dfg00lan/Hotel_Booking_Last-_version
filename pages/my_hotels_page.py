import streamlit as st
from tools.db import fetch_partner_hotels, delete_hotel_owned

def render(goto):
    st.title("🏨 Мои объекты")

    user = st.session_state.get("user")
    if not user:
        st.error("Войдите в систему.")
        return
    if user.get("role") not in ("partner", "admin"):
        st.error("Доступ только для партнёров.")
        return

    partner_id = user["id"]
    is_admin = user.get("role") == "admin"

    hotels = fetch_partner_hotels(partner_id)

    # шапка-статистика
    st.markdown(
        f"**Отелей:** {len(hotels)} "
    )
    st.divider()

    # список отелей
    with st.expander("Мои отели", expanded=True):
        if not hotels:
            st.info("У вас пока нет отелей. Добавьте отель или назначьте owner_id в сид-данных.")
        else:
            for (hid, name, city, price, rating, rooms, available) in hotels:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(
                        f"**{name}** ({city})  \n"
                        f"Комнат: {rooms} • Доступно: {available} • Цена: {price:.0f} • Рейтинг: ⭐ {rating:.1f}"
                    )
                # Шаг 1: запрос на удаление
                    if st.button("🗑️ Удалить", key=f"ask_del_{hid}"):
                        st.session_state[f"confirm_del_{hid}"] = True

                # Шаг 2: подтверждение под карточкой
                if st.session_state.get(f"confirm_del_{hid}"):
                    st.warning(f"Удалить отель **{name}** и все его бронирования? Это действие необратимо.")
                    col_ok, col_cancel = st.columns(2)
                    with col_ok:
                        if st.button("✅ Да, удалить", key=f"do_del_{hid}"):
                            ok = delete_hotel_owned(hid, partner_id, is_admin=is_admin)
                            if ok:
                                st.success("Отель удалён.")
                                st.session_state.pop(f"confirm_del_{hid}", None)
                                st.rerun()
                            else:
                                st.error("Не удалось удалить (нет прав или отель не найден).")
                                st.session_state.pop(f"confirm_del_{hid}", None)
                    with col_cancel:
                        if st.button("✖ Отмена", key=f"cancel_del_{hid}"):
                            st.session_state.pop(f"confirm_del_{hid}", None)
                
    st.divider()

    