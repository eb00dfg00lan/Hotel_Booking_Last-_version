import streamlit as st
from datetime import date, timedelta
from tools.db import fetch_hotels, insert_booking

def render(goto):
    st.title("Бронирование")
    if not st.session_state.get("user"):
        st.error("Сначала войдите в систему.")
        return

    sel_id = st.session_state.get("selected_hotel_id")
    if not sel_id:
        st.info("Сначала выберите отель в поиске.")
        if st.button("← К поиску"):
            goto("search")
        return

    rows = fetch_hotels() or []
    row = next((r for r in rows if int(r[0]) == int(sel_id)), None)
    if not row:
        st.error("Отель не найден.")
        st.session_state.selected_hotel_id = None
        if st.button("← К поиску"):
            goto("search")
        return

    h = {"id": int(row[0]), "name": row[1], "city": row[2], "price": int(row[3]),
         "rating": float(row[4]), "rooms": int(row[5]), "available": bool(row[6])}

    st.markdown(f"### {h['name']} — {h['city']}")
    ci_key = f"ci_{h['id']}"; co_key = f"co_{h['id']}"; gu_key = f"gu_{h['id']}"
    check_in = st.date_input("Дата заезда", min_value=date.today(), key=ci_key)
    min_co = max(check_in + timedelta(days=1), date.today() + timedelta(days=1))
    check_out = st.date_input("Дата выезда", min_value=min_co, key=co_key)
    guests = st.number_input("Гостей", 1, 10, key=gu_key)

    nights = max((check_out - check_in).days, 0)
    total_price = h["price"] * nights if nights > 0 else 0
    st.info(f"Итого за {nights} ноч.: **{total_price} ₸**")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Подтвердить", key=f"confirm_{h['id']}"):
            if nights <= 0:
                st.error("Выезд должен быть позже заезда минимум на 1 день.")
            else:
                insert_booking(
                    st.session_state["user"]["id"], h["id"],
                    check_in.isoformat(), check_out.isoformat(), int(guests)
                )
                st.success("Бронирование создано.")
                st.session_state.selected_hotel_id = None
                goto("bookings")
    with c2:
        if st.button("← Назад к поиску"):
            goto("search")