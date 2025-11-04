# tools/db.py
import sqlite3
import json
from datetime import date
from pathlib import Path
from typing import Iterable, Optional, Tuple, List

from tools.utils import load_json

# Эти датаклассы используются, чтобы вернуть данные в удобной форме
from core.domain import Price, Availability, Rule
# Нужен для выборки диапазона дат под календарную сетку (6 недель)
from core.dates import month_grid_bounds

DB_PATH = Path("Data/hotel_booking.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Полезно, чтобы получать dict-подобные результаты при желании
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('guest', 'partner', 'admin'))
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS hotels (
                id INTEGER PRIMARY KEY,
                name TEXT,
                city TEXT,
                price REAL,
                rating REAL,
                rooms INTEGER,
                available INTEGER,
                roomtype TEXT NOT NULL,                 -- CSV или JSON-строка-массив
                rateplan TEXT NOT NULL,                 -- CSV или JSON-строка-массив
                amenities TEXT NOT NULL DEFAULT '{}',
                owner_id INTEGER
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                hotel_id INTEGER,
                check_in TEXT,
                check_out TEXT,
                guests INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(hotel_id) REFERENCES hotels(id)
            );
        """)

        # Индексы для скорости фильтров
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hotels_city ON hotels(city);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_hotels_owner ON hotels(owner_id);")
        conn.commit()

    # Доп. таблицы под price-календарь
    ensure_calendar_tables()


# ---------- Блок price-календаря: таблицы/миграции ----------
def ensure_calendar_tables():
    """Создаёт таблицы и индексы под календарь цен/доступности/правил."""
    with get_connection() as conn:
        cur = conn.cursor()

        # room_types / rate_plans вы можете хранить отдельно; для календаря достаточно связок ids
        cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            rate_id INTEGER NOT NULL,
            date TEXT NOT NULL,          -- 'YYYY-MM-DD'
            amount INTEGER NOT NULL,     -- сумма в тыйын/копейках
            currency TEXT NOT NULL
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_prices_rate_date ON prices(rate_id, date);")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY,
            room_type_id INTEGER NOT NULL,
            date TEXT NOT NULL,          -- 'YYYY-MM-DD'
            available INTEGER NOT NULL   -- остаток на дату
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_avail_rt_date ON availability(room_type_id, date);")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY,
            kind TEXT NOT NULL,          -- 'min_stay' | 'max_stay' | 'cta' | 'ctd'
            payload TEXT NOT NULL        -- JSON: {"room_type_id":int,"rate_id":int,"value":..., "date":"YYYY-MM-DD"}
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_rules_kind ON rules(kind);")

        conn.commit()


# ---------- Сервис для CSV/JSON полей в hotels ----------
def _list_to_csv(value) -> Optional[str]:
    """Нормализует list -> CSV (или строку/None)."""
    if value is None:
        return None
    if isinstance(value, list):
        items = [str(t).strip() for t in value if t is not None and str(t).strip()]
        return ",".join(items)
    if isinstance(value, str):
        return value.strip() or None
    return str(value)


# ---------- Засев БД из seed.json ----------
def seed_database(seed_path: str = "Data/seed.json"):
    """Засев БД из JSON.
    Поддерживает, что в seed у отелей roomtype/rateplan могут быть списками.
    Мы кладём их в БД в формате CSV (совместимо с текущими фильтрами).
    Также вставляем owner_id.
    Дополнительно: загружаем prices/availability/rules, если присутствуют.
    """
    data = load_json(seed_path)
    if not data:
        return

    ensure_calendar_tables()

    with get_connection() as conn:
        cur = conn.cursor()

        # --- hotels
        for h in data.get("hotels", []):
            roomtype_str = _list_to_csv(h.get("roomtype"))
            rateplan_str = _list_to_csv(h.get("rateplan"))
            amenities_str = h.get("amenities") if isinstance(h.get("amenities"), str) else "{}"
            owner_id = h.get("owner_id")

            cur.execute("""
                INSERT OR IGNORE INTO hotels
                (id, name, city, price, rating, rooms, available, roomtype, rateplan, amenities, owner_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h["id"], h.get("name"), h.get("city"), h.get("price"), h.get("rating"),
                h.get("rooms"), int(h.get("available", 0)), roomtype_str, rateplan_str,
                amenities_str, owner_id
            ))

        # --- users
        for u in data.get("users", []):
            cur.execute("""
                INSERT OR IGNORE INTO users (id, username, email, password, role)
                VALUES (?, ?, ?, ?, ?)
            """, (u["id"], u["username"], u["email"], u["password"], u["role"]))

        # --- bookings
        for b in data.get("bookings", []):
            cur.execute("""
                INSERT OR IGNORE INTO bookings (id, user_id, hotel_id, check_in, check_out, guests)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (b["id"], b["user_id"], b["hotel_id"], b["check_in"], b["check_out"], b["guests"]))

        # --- prices (для календаря)
        for p in data.get("prices", []):
            cur.execute("""
                INSERT OR REPLACE INTO prices(id, rate_id, date, amount, currency)
                VALUES(?,?,?,?,?)
            """, (p.get("id"), p["rate_id"], p["date"], p["amount"], p.get("currency", "KZT")))

        # --- availability (для календаря)
        for a in data.get("availability", []):
            cur.execute("""
                INSERT OR REPLACE INTO availability(id, room_type_id, date, available)
                VALUES(?,?,?,?)
            """, (a.get("id"), a["room_type_id"], a["date"], a["available"]))

        # --- rules (для календаря)
        for r in data.get("rules", []):
            cur.execute("""
                INSERT OR REPLACE INTO rules(id, kind, payload)
                VALUES(?,?,?)
            """, (r.get("id"), r["kind"], json.dumps(r.get("payload", {}))))

        conn.commit()


# ---------- Поиск отелей с фильтрами ----------
def _add_token_filters_sql(
    base_query_parts: list[str],
    params: list,
    column: str,
    tokens: Iterable[str],
    require_all: bool
):
    """
    Добавляет условия поиска токенов в колонке, которая может хранить CSV или JSON-массив.
    Поддерживаются два варианта:
      1) CSV: ',val1,val2,' и поиск через instr(','||col||',', ','||?||',')>0
      2) JSON: '["val1","val2"]' и поиск через instr(col, '"'||?||'"')>0
    """
    tokens = [t for t in (tokens or []) if str(t).strip()]
    if not tokens:
        return

    groups = []
    for t in tokens:
        # Один токен: найдём его либо как CSV-ячейку, либо как JSON-элемент в кавычках
        groups.append(
            f"(instr(',' || COALESCE({column}, '') || ',', ',' || ? || ',') > 0 "
            f"OR instr(COALESCE({column}, ''), '\"' || ? || '\"') > 0)"
        )
        params.extend([t, t])

    if require_all:
        # Все токены должны встретиться
        for g in groups:
            base_query_parts.append(" AND " + g)
    else:
        # Достаточно любого из списка
        base_query_parts.append(" AND (" + " OR ".join(groups) + ")")


def fetch_hotels(
    city: str = None,
    max_price: float = None,
    any_types: Optional[list[str]] = None,
    all_types: Optional[list[str]] = None,
    any_plans: Optional[list[str]] = None,
    all_plans: Optional[list[str]] = None
):
    """
    Поиск отелей с поддержкой фильтров:
      - city: точное совпадение города
      - max_price: цена <= max_price
      - any_types: хотя бы один тип комнаты из списка
      - all_types: содержать все типы комнаты из списка
      - any_plans: хотя бы один тариф из списка
      - all_plans: содержать все тарифы из списка

    Колонки roomtype/rateplan могут содержать CSV или JSON-массив — обе формы поддержаны.
    """
    with get_connection() as conn:
        cur = conn.cursor()
        query_parts = [
            "SELECT id, name, city, price, rating, rooms, available, roomtype, rateplan, owner_id",
            "FROM hotels",
            "WHERE 1=1"
        ]
        params: list = []

        if city:
            query_parts.append(" AND city = ?")
            params.append(city)

        if max_price is not None:
            query_parts.append(" AND price <= ?")
            params.append(max_price)

        if any_types:
            _add_token_filters_sql(query_parts, params, "roomtype", any_types, require_all=False)

        if all_types:
            _add_token_filters_sql(query_parts, params, "roomtype", all_types, require_all=True)

        if any_plans:
            _add_token_filters_sql(query_parts, params, "rateplan", any_plans, require_all=False)

        if all_plans:
            _add_token_filters_sql(query_parts, params, "rateplan", all_plans, require_all=True)

        query = " ".join(query_parts)
        cur.execute(query, tuple(params))
        return cur.fetchall()


def insert_booking(user_id: int, hotel_id: int, check_in: str, check_out: str, guests: int) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings (user_id, hotel_id, check_in, check_out, guests)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, hotel_id, check_in, check_out, guests))
        conn.commit()
        return cur.lastrowid


def fetch_user_by_email(email: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, password, role FROM users WHERE email = ?", (email,))
        return cur.fetchone()


def fetch_partner_hotels(partner_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, city, price, rating, rooms, available
            FROM hotels
            WHERE owner_id = ?
            ORDER BY name
        """, (partner_id,))
        return cur.fetchall()


def fetch_partner_bookings(partner_id: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.id          AS booking_id,
                h.id          AS hotel_id,
                h.name        AS hotel_name,
                h.city        AS city,
                b.check_in,
                b.check_out,
                b.guests,
                h.price,
                h.rating
            FROM bookings b
            JOIN hotels h ON h.id = b.hotel_id
            WHERE h.owner_id = ?
            ORDER BY b.id DESC
        """, (partner_id,))
        return cur.fetchall()


def delete_hotel_owned(hotel_id: int, owner_id: int, is_admin: bool = False) -> bool:
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        cur.execute("SELECT owner_id FROM hotels WHERE id = ?", (hotel_id,))
        row = cur.fetchone()
        if not row:
            return False

        real_owner_id = row[0]
        if not is_admin and real_owner_id != owner_id:
            return False

        cur.execute("DELETE FROM bookings WHERE hotel_id = ?", (hotel_id,))
        cur.execute("DELETE FROM hotels WHERE id = ?", (hotel_id,))
        conn.commit()
        return cur.rowcount > 0


def delete_booking_owned(booking_id: int, owner_id: int, is_admin: bool = False) -> bool:
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        cur.execute("""
            SELECT h.owner_id
            FROM bookings b
            JOIN hotels h ON b.hotel_id = h.id
            WHERE b.id = ?
        """, (booking_id,))
        row = cur.fetchone()
        if not row:
            return False

        real_owner_id = row[0]
        if not is_admin and real_owner_id != owner_id:
            return False

        cur.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()
        return cur.rowcount > 0


def insert_hotel(
    owner_id: int,
    name: str,
    city: str,
    price: float,
    rating: float,
    rooms: int,
    available: int,
    roomtype: str,   # JSON-строка ИЛИ CSV
    rateplan: str,   # JSON-строка ИЛИ CSV
    amenities: str = "{}"
) -> Optional[int]:
    """Вставка отеля. Принимает roomtype/rateplan как JSON-строки или CSV.
    Хранение — как есть (фильтры поддерживают оба варианта).
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO hotels (
                  owner_id, name, city, price, rating, rooms, available,
                  roomtype, rateplan, amenities
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    owner_id, name, city, price, rating, rooms, available,
                    roomtype, rateplan, amenities
                ),
            )
            conn.commit()
            return cur.lastrowid
    except Exception as e:
        print("insert_hotel error:", repr(e))
        return None


# ---------- Выборки под price-календарь ----------
def fetch_prices_for_calendar(rate_id: int, month_start: date) -> Tuple[Price, ...]:
    """Возвращает цены для rate_id в пределах календарной сетки месяца (6 недель)."""
    ensure_calendar_tables()
    grid_start, grid_end = month_grid_bounds(month_start)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, rate_id, date, amount, currency
            FROM prices
            WHERE rate_id = ?
              AND date >= ?
              AND date < ?
            ORDER BY date ASC
        """, (rate_id, grid_start.isoformat(), grid_end.isoformat()))
        rows = cur.fetchall()
    items: List[Price] = [Price(int(r[0]), int(r[1]), r[2], int(r[3]), r[4]) for r in rows]
    return tuple(items)


def fetch_availability_for_calendar(room_type_id: int, month_start: date) -> Tuple[Availability, ...]:
    """Возвращает доступность для room_type_id в пределах календарной сетки месяца (6 недель)."""
    ensure_calendar_tables()
    grid_start, grid_end = month_grid_bounds(month_start)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, room_type_id, date, available
            FROM availability
            WHERE room_type_id = ?
              AND date >= ?
              AND date < ?
            ORDER BY date ASC
        """, (room_type_id, grid_start.isoformat(), grid_end.isoformat()))
        rows = cur.fetchall()
    items: List[Availability] = [Availability(int(r[0]), int(r[1]), r[2], int(r[3])) for r in rows]
    return tuple(items)


def fetch_rules_for_rate(room_type_id: int, rate_id: int) -> Tuple[Rule, ...]:
    """Возвращает правила, подходящие под room_type_id/rate_id (фильтр в Python)."""
    ensure_calendar_tables()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, kind, payload FROM rules")
        rows = cur.fetchall()
    out: List[Rule] = []
    for r in rows:
        try:
            payload = json.loads(r[2]) if r[2] else {}
        except Exception:
            payload = {}
        # Если payload пуст — считаем глобальным правилом
        if payload:
            if payload.get("room_type_id") not in (None, room_type_id):
                continue
            if payload.get("rate_id") not in (None, rate_id):
                continue
        out.append(Rule(int(r[0]), r[1], payload))
    return tuple(out)


if __name__ == "__main__":
    init_db()
