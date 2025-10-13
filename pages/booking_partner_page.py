# бронирования по моим отелям
import streamlit as st
from tools.db import fetch_partner_bookings, delete_booking_owned

def render(goto):
    st.subheader("Бронирования")

    user = st.session_state.get("user")
    if not user:
        st.error("Войдите в систему.")
        return
    if user.get("role") not in ("partner", "admin"):
        st.error("Доступ только для партнёров.")
        return

    partner_id = user["id"]
    is_admin = user.get("role") == "admin"

    rows = fetch_partner_bookings(partner_id)
    # ожидаемый порядок: (booking_id, hotel_id, hotel_name, city, check_in, check_out, guests, price, rating)

    with st.expander("Бронирования", expanded=True):
        if not rows:
            st.info("Бронирований нет")
            return

        for (bid, hid, hname, city, ci, co, guests, price, rating) in rows:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.write(f"🆔{bid} | 🏨 {hname} ({city}) | {ci} → {co} | 👥 {guests} | 💵 {int(price)} | ⭐ {rating:.1f}")
            with c2:
                # Шаг 1: запрос на удаление (ставим флаг по booking_id)
                if st.button("🗑️ Удалить", key=f"book_del_{bid}"):
                    st.session_state[f"confirm_book_del_{bid}"] = True

            # Шаг 2: подтверждение под карточкой (по booking_id)
            if st.session_state.get(f"confirm_book_del_{bid}"):
                st.warning("Удалить бронирование? Это действие необратимо.")
                col_ok, col_cancel = st.columns(2)
                with col_ok:
                    if st.button("✅ Да, удалить", key=f"do_book_del_{bid}"):
                        ok = delete_booking_owned(bid, partner_id, is_admin=is_admin)
                        if ok:
                            st.success("Бронирование удалено.")
                            st.session_state.pop(f"confirm_book_del_{bid}", None)
                            st.rerun()
                        else:
                            st.error("Не удалось удалить (нет прав или бронирование не найдено).")
                            st.session_state.pop(f"confirm_book_del_{bid}", None)
                with col_cancel:
                    if st.button("✖ Отмена", key=f"cancel_book_del_{bid}"):
                        st.session_state.pop(f"confirm_book_del_{bid}", None)
