## Project Codemap: Sri Vengamamba Food Court

### Overview
Flask-based local billing app with a desktop wrapper. SQLite stores menu, bills, settings, and logs. Frontend uses Bootstrap and vanilla JS; templates render views, JS calls JSON APIs.

### Backend (Python)

- `app.py`
  - App setup: secret key, upload config, ensures `static/images` and `database` exist.
  - DB helpers: `get_db_connection()` (WAL mode, retry/backoff), `safe_db_operation()`, `check_and_fix_database()`.
  - Auth decorators: `login_required`, `admin_required`, `user_required` (session-based gatekeeping).
  - Schema/init: `init_db()` creates tables `menu`, `daily_sequence`, `bill_sequence`, `bills`, `settings`, `user_login_logs`, `user_activity_logs`; seeds default `settings`.
  - Settings helpers: `get_setting(key)`, `set_setting(key, value)`.
  - Logging helpers: `log_user_login`, `log_user_logout`, `log_user_activity`.
  - Routes (HTML):
    - `GET /login` + `POST /login`: simple credential check; sets `session` and logs login.
    - `GET /logout`: logs logout, clears session.
    - `GET /` root: redirects to `login`, `index` or `user_dashboard`.
    - `GET /billing` (`index`): main billing UI; loads categories and menu items.
    - `GET /menu` (`menu_management`): admin menu management.
    - `GET /reports`: admin sales and bills history.
    - `GET /settings`: admin settings UI.
    - `GET /user_dashboard`: limited-access user dashboard.
    - `GET /unauthorized`: unauthorized page.
    - `GET /bill/<bill_number>`: printable bill view.
  - Routes (JSON APIs):
    - `POST /test-login`: echo test.
    - `GET /api/user_dashboard`: dashboard stats for today.
    - `GET /api/all_menu_items`: all menu items for preload.
    - `GET /api/menu_items/<category>`: items by category.
    - `POST /api/add_menu_item`: add item (optional image upload).
    - `POST /api/update_menu_item/<int:id>`: update item (optional new image).
    - `DELETE /api/delete_menu_item/<int:id>`: delete item.
    - `POST /api/generate_bill`: compute totals, generate daily sequence and bill number, persist bill + mapping, log activity; returns numbers for printing.
    - `POST /api/update_settings`: persist settings; logs activity.
    - `GET /api/settings`: returns all settings.
    - `GET /api/user_logs`: latest login/activity logs (admin).
    - `GET /api/check_database`: checks/attempts fix (admin).
    - `GET /api/item_analysis`: item sales aggregation over date range (admin).
    - `GET /api/test_bill_number`: preview next bill number (admin).

- `launcher.py`
  - Desktop app using `pywebview` to embed the web UI.
  - Sets CWD to executable directory, starts Flask app in a background thread, waits for readiness, creates a resizable window pointing to `http://127.0.0.1:5000`.
  - Basic logging to `app_log.txt`; shows native message box on critical error; `cleanup()` attempts to kill python processes on exit.

- `desktop_launcher.py`
  - Alternative desktop launcher using Tkinter GUI that starts Flask in background and opens default browser to `http://127.0.0.1:5000` once ready.

- `build_exe.py`
  - Build pipeline: creates `.spec`, installs requirements, cleans `build/` and `dist/`, runs PyInstaller, assembles `SriVengamambaFoodCourt_Distribution/` with exe, assets, database, templates, and a README.

- `setup.py`
  - Developer setup: checks Python version, creates directories, downloads Bootstrap assets if missing, installs requirements, and prints how to run.

- `download_bootstrap.py`, `download_fonts.py`
  - Utility scripts to pull Bootstrap CSS/JS and icon fonts for offline use.

### Database (SQLite)

- File: `database/restaurant.db`.
- Key tables:
  - `menu(id, name, name_te, category, price, image, description, description_te, created_at)`
  - `bills(id, bill_number, items(JSON), subtotal, tax_amount, service_charge, total, created_at)`
  - `daily_sequence(seq_date, last_seq)` for per-day bill sequences
  - `bill_sequence(bill_number, seq_date, seq_number)` mapping
  - `settings(key, value, updated_at)`
  - `user_login_logs(username, role, login_time, logout_time, session_duration, ip_address, user_agent)`
  - `user_activity_logs(username, activity_type, activity_description, bill_number, created_at)`

### Frontend

- Templates (`templates/`)
  - `base.html`: main layout, navbar with role-aware links, flash messages, footer, includes `bootstrap.min.css`, `bootstrap-icons.css`, `style.css`, `bootstrap.bundle.min.js`, `language.js`, `main.js`.
  - `base_login.html`: minimal base for unauthenticated pages.
  - `login.html`: login form; JS posts to `/login` and handles redirects to billing or dashboard based on role.
  - `billing.html`: three-pane layout (categories, items grid, bill preview). Includes bill confirmation modal.
  - `menu.html`: admin item management (uses JS modals for add/edit/delete).
  - `reports.html`: bills list and aggregates with month filtering.
  - `settings.html`: form to edit tax/service rates and restaurant info.
  - `bill_print.html`: printable bill for a `bill_number`.
  - `unauthorized.html`, `user_dashboard.html`: misc views.

- Static JS (`static/js/`)
  - `main.js`:
    - Caches and displays menu items; universal search across all items.
    - Manages current bill in-memory; updates totals using settings; opens bill print window after `/api/generate_bill`.
    - Menu management: add/update/delete items via corresponding endpoints; image preview utility.
    - Settings update via `/api/update_settings`.
    - Alert utility and minor UI helpers.
  - `language.js`:
    - Simple i18n (English/Telugu) for UI strings using `data-lang` attributes; persists choice in `localStorage`.

- Static CSS/Assets (`static/`)
  - `css/bootstrap.min.css`, `css/bootstrap-icons.css`, `css/style.css`
  - Icon fonts under `css/fonts/`
  - Images under `static/images/` (uploads + placeholders)

### Key Flows

- Authentication
  - POST `/login` with `username`, `password` → sets session and returns JSON with `redirect_url`.
  - `logout` clears session; admin routes require `session.role == 'admin'`.

- Billing
  - Frontend loads settings and all items; user adds items to in-memory `currentBill`.
  - Confirm modal shows breakdown; POST `/api/generate_bill` persists bill and returns `bill_number`.
  - Opens `/bill/<bill_number>` for printing.

- Menu Management (admin)
  - Add/update/delete items via respective endpoints; optional image upload stored to `static/images/`.

- Reports (admin)
  - Server aggregates totals and lists bills with optional month filter; template displays metrics and history.

### Noted Inconsistencies/Risks (worth fixing)

- API path mismatch in frontend:
  - `main.js` initial `loadSettings()` calls `/api/get_settings` (does not exist). Later `loadSettings()` (redeclared) calls `/api/settings` (exists). Consolidate to one function using `/api/settings`.

- `api_user_dashboard` in `app.py` selects `SUM(total_amount)` but `bills` table uses column `total`. Should use `SUM(total)`.

- `api/item_analysis` selects `bill_items` but persisted column is `items`. Adjust selects accordingly.

- Minor: Some routes open SQLite connections directly while others use `safe_db_operation`; consider standardizing for consistency and error handling.

### How to Run

- Dev: `python app.py` then open `http://localhost:5000`.
- Desktop: run `dist/SriVengamambaFoodCourt.exe` or the launcher scripts.


