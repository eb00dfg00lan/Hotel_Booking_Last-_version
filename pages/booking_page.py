import secrets
from typing import cast
import streamlit as st
from datetime import date, timedelta

from tools.db import fetch_hotels, insert_booking

# наш «контейнер» (валидатор+Either)
from core.container import  Booking
from core.container import Either, validate_booking, quote_amount
from pages import booking_guest_page
# (опционально, если будешь считать по реальным Price/Availability/Rule)
# from core.offers import quote_offer
# from core.domain import Price, Availability, Rule


def render(goto):
    st.title("Бронирование")
    ss = st.session_state
    if "confirm_ctx" not in ss: 
        ss.confirm_ctx = None        # { "booking": Booking, "total": int, "tx_key": str, "nonce": str }
    if "last_committed_key" not in ss: 
        ss.last_committed_key = None

    if not ss.get("user"):
        st.error("Сначала войдите в систему.")
        return

    sel_id = ss.get("selected_hotel_id")
    if not sel_id:
        st.info("Сначала выберите отель в поиске.")
        if st.button("← К поиску"):
            goto("search")
        return

    rows = fetch_hotels() or []
    row = next((r for r in rows if int(r[0]) == int(sel_id)), None)
    if not row:
        st.error("Отель не найден.")
        ss.selected_hotel_id = None
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
            # 1) собираем черновик
            draft = Booking(
                user_id=ss["user"]["id"],
                hotel_id=h["id"],
                check_in=check_in,
                check_out=check_out,
                guests=int(guests),
                nightly_price=int(h["price"]),
            )
            # 2) валидируем и считаем сумму (Either)
            result = (
                validate_booking(draft)                     # Either[dict, Booking]
                .map(lambda b: (b, quote_amount(b)))        # Either[dict, tuple[Booking,int]]
            )

            if not result.is_right:
                err = cast(dict, result.get_or_else({}))
                for k, v in err.items():
                    st.error(f"❌ {k}: {v}")
            else:
                b, total = result.get_or_else((None, 0))
                # 3) запускаем ПАНЕЛЬ ПОДТВЕРЖДЕНИЯ (а не пишем в БД сразу)
                tx_key = f"{b.user_id}:{b.hotel_id}:{b.check_in.isoformat()}:{b.check_out.isoformat()}:{b.guests}"
                ss.confirm_ctx = {
                    "booking": b,
                    "total": total,
                    "tx_key": tx_key,
                    "nonce": secrets.token_hex(3),
                }

    with c2:
        if st.button("← Назад к поиску"):
            goto("search")

    # --- ПАНЕЛЬ ПОДТВЕРЖДЕНИЯ ---
    if ss.confirm_ctx:
        ctx = ss.confirm_ctx
        b: Booking = ctx["booking"]
        total = ctx["total"]
        tx_key = ctx["tx_key"]
        nonce = ctx["nonce"]

        st.markdown("---")
        with st.container(border=True):
            st.subheader("Подтверждение бронирования")
            st.write(f"**Отель:** {h['name']} ({h['city']})")
            st.write(f"**Даты:** {b.check_in.isoformat()} → {b.check_out.isoformat()}  •  **Ночей:** {(b.check_out - b.check_in).days}")
            st.write(f"**Гостей:** {b.guests}")
            st.write(f"**Сумма:** **{total} ₸**")

            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("✅ Да, подтвердить", key=f"confirm_yes_{nonce}"):
                    # идемпотентность
                    if ss.last_committed_key != tx_key:
                        insert_booking(
                            b.user_id, b.hotel_id,
                            b.check_in.isoformat(), b.check_out.isoformat(),
                            b.guests
                        )
                        ss.last_committed_key = tx_key
                    st.success("Бронирование создано.")
                    ss.selected_hotel_id = None
                    ss.confirm_ctx = None
                    goto(booking_guest_page)

            with cc2:
                if st.button("↩ Отмена", key=f"confirm_cancel_{nonce}"):
                    ss.confirm_ctx = None
                    st.info("Подтверждение отменено.")
