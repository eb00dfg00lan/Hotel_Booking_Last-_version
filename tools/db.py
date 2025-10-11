import sqlite3
from pathlib import Path
from tools.utils import load_json

DB_PATH = Path("Data/hotel_booking.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


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
                roomtype TEXT,
                rateplan TEXT
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
        conn.commit()


def seed_database(seed_path: str = "Data/seed.json"):
    data = load_json(seed_path)
    if not data:
        return

    with get_connection() as conn:
        cur = conn.cursor()

        # --- hotels
        for h in data.get("hotels", []):
            # roomtype может быть списком или строкой
            rt = h.get("roomtype")
            if isinstance(rt, list):
                roomtype_str = ",".join(t.strip() for t in rt if t and str(t).strip())
            elif isinstance(rt, str):
                roomtype_str = rt.strip()
            else:
                roomtype_str = None

            # rateplan тоже может быть списком или строкой (ОТДЕЛЬНО от roomtype!)
            rp = h.get("rateplan")
            if isinstance(rp, list):
                rateplan_str = ",".join(t.strip() for t in rp if t and str(t).strip())
            elif isinstance(rp, str):
                rateplan_str = rp.strip()
            else:
                rateplan_str = None

            # ВАЖНО: число плейсхолдеров должно совпадать с числом колонок
            cur.execute("""
                    INSERT OR IGNORE INTO hotels
                    (id, name, city, price, rating, rooms, available, roomtype, rateplan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h["id"], h["name"], h["city"], h["price"], h["rating"],
                h["rooms"], int(h["available"]), roomtype_str, rateplan_str
            ))

        # --- users
        for u in data.get("users", []):
            cur.execute("""
                INSERT OR IGNORE INTO users (id, username, email, password,role)
                VALUES (?, ?, ?, ?, ?)
            """, (u["id"], u["username"], u["email"], u["password"],u["role"]))

        # --- bookings
        for b in data.get("bookings", []):
            cur.execute("""
                INSERT OR IGNORE INTO bookings (id, user_id, hotel_id, check_in, check_out, guests)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (b["id"], b["user_id"], b["hotel_id"], b["check_in"], b["check_out"], b["guests"]))

        conn.commit()


def fetch_hotels(city: str = None, max_price: float = None,any_types: list[str] | None = None,
                 all_types: list[str] | None = None,any_plans: list[str] | None = None,
                 all_plans: list[str] | None = None):
    with get_connection() as conn:
        cur = conn.cursor()
        query = "SELECT id, name, city, price, rating, rooms, available,roomtype,rateplan FROM hotels WHERE 1=1"
        params = []
        if city:
            query += " AND city = ?"
            params.append(city)
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        if any_types:
            parts = []
            for t in any_types:
                parts.append("instr(',' || COALESCE(roomtype,'') || ',', ',' || ? || ',') > 0")
                params.append(t)
            query += " AND (" + " OR ".join(parts) + ")"
        if all_types:
            for t in all_types:
                query += " AND instr(',' || COALESCE(roomtype,'') || ',', ',' || ? || ',') > 0"
                params.append(t)
        if any_plans:
            parts = []
            for t in any_plans:
                parts.append("instr(',' || COALESCE(rateplan,'') || ',', ',' || ? || ',') > 0")
                params.append(t)
            query += " AND (" + " OR ".join(parts) + ")"
        if all_plans:
            for t in all_plans:
                query += " AND instr(',' || COALESCE(rateplan,'') || ',', ',' || ? || ',') > 0"
                params.append(t)
        cur.execute(query, tuple(params))
        return cur.fetchall()


def insert_booking(user_id: int, hotel_id: int, check_in: str, check_out: str, guests: int):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings (user_id, hotel_id, check_in, check_out, guests)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, hotel_id, check_in, check_out, guests))
        conn.commit()


def fetch_user_by_email(email: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, email FROM users WHERE email = ?", (email,))
        return cur.fetchone()
    
if __name__ == "__main__":
    init_db()

