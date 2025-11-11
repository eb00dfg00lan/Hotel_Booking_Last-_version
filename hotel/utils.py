from pathlib import Path
def init_db_if_needed():
    try:
        from tools.db import init_db, seed_database
        init_db()
        seed_database()
    except Exception as e:
        print('init_db_if_needed:', e)

def ensure_session_defaults(request):
    ss = request.session
    if 'page' not in ss:
        ss['page'] = 'welcome'
    if 'user' not in ss:
        ss['user'] = None
    if 'selected_hotel_id' not in ss:
        ss['selected_hotel_id'] = None
    if 'role' not in ss:
        ss['role'] = 'guest'
