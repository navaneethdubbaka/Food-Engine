from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
import sqlite3
import os
from datetime import datetime, date
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import threading
import time

app = Flask(__name__)
app.secret_key = 'restaurant_billing_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('database', exist_ok=True)

# Database connection lock for thread safety
db_lock = threading.Lock()

def get_db_connection():
    """Get a database connection with proper error handling and timeout"""
    max_retries = 3
    retry_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            with db_lock:
                conn = sqlite3.connect('database/restaurant.db', timeout=10.0)
                # Enable WAL mode for better concurrency
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                conn.execute('PRAGMA cache_size=1000')
                conn.execute('PRAGMA temp_store=MEMORY')
                return conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                print(f"Database locked, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Database error: {e}")
                raise e
        except Exception as e:
            print(f"Unexpected database error: {e}")
            raise e
    
    raise sqlite3.OperationalError("Could not acquire database lock after multiple attempts")

def safe_db_operation(operation_func, *args, **kwargs):
    """Safely execute database operations with proper connection management"""
    conn = None
    try:
        conn = get_db_connection()
        result = operation_func(conn, *args, **kwargs)
        conn.commit()
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database operation failed: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def check_and_fix_database():
    """Check and fix database lock issues"""
    try:
        # Try to connect and check database integrity
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if database is accessible
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        
        # Check for any locks
        cursor.execute('PRAGMA database_list')
        databases = cursor.fetchall()
        
        conn.close()
        print("Database is accessible and not locked")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print("Database is locked, attempting to fix...")
            try:
                # Try to force unlock by creating a new connection with immediate mode
                conn = sqlite3.connect('database/restaurant.db', timeout=1.0)
                conn.execute('PRAGMA journal_mode=DELETE')  # Switch to DELETE mode to release locks
                conn.execute('PRAGMA journal_mode=WAL')     # Switch back to WAL mode
                conn.close()
                print("Database lock released")
                return True
            except Exception as fix_error:
                print(f"Could not fix database lock: {fix_error}")
                return False
        else:
            print(f"Database error: {e}")
            return False
    except Exception as e:
        print(f"Unexpected database error: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Authentication functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('unauthorized'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    
    # Menu items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_te TEXT,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            description TEXT,
            description_te TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add translation columns if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE menu ADD COLUMN name_te TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE menu ADD COLUMN description_te TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Sequences to support daily sequence numbers for bills
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_sequence (
            seq_date TEXT PRIMARY KEY,
            last_seq INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill_sequence (
            bill_number TEXT PRIMARY KEY,
            seq_date TEXT NOT NULL,
            seq_number INTEGER NOT NULL
        )
    ''')
    
    # Bills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT UNIQUE NOT NULL,
            items TEXT NOT NULL,
            subtotal REAL NOT NULL,
            tax_amount REAL NOT NULL,
            service_charge REAL NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User login logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logout_time TIMESTAMP,
            session_duration INTEGER,
            ip_address TEXT,
            user_agent TEXT
        )
    ''')
    
    # User activity logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            activity_description TEXT NOT NULL,
            bill_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table for proper user management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default settings if not exists
    default_settings = [
        ('tax_rate', '10.0'),
        ('service_charge_rate', '5.0'),
        ('restaurant_name', 'My Restaurant'),
        ('restaurant_address', '123 Main Street, City'),
        ('restaurant_phone', '+1-234-567-8900'),
        ('restaurant_gst', '')
    ]
    
    for key, value in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
    
    # Insert default users if not exists
    default_users = [
        ('admin', 'admin123', 'admin'),
        ('user', 'user123', 'user')
    ]
    
    for username, password, role in default_users:
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            password_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                         (username, password_hash, role))
    
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """Get a setting value from database"""
    def _get_setting(conn):
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else default
    
    try:
        return safe_db_operation(_get_setting)
    except Exception as e:
        print(f"Error getting setting {key}: {e}")
        return default

def set_setting(key, value):
    """Set a setting value in database"""
    def _set_setting(conn):
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', (key, value))
        return True
    
    try:
        return safe_db_operation(_set_setting)
    except Exception as e:
        print(f"Error setting {key}: {e}")
        return False

def log_user_login(username, role, ip_address=None, user_agent=None):
    """Log user login"""
    def _log_login(conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_login_logs (username, role, ip_address, user_agent)
            VALUES (?, ?, ?, ?)
        ''', (username, role, ip_address, user_agent))
        return True
    
    try:
        return safe_db_operation(_log_login)
    except Exception as e:
        print(f"Error logging user login: {e}")
        return False

def log_user_logout(username):
    """Log user logout and calculate session duration"""
    def _log_logout(conn):
        cursor = conn.cursor()
        
        # Get the latest login for this user
        cursor.execute('''
            SELECT id, login_time FROM user_login_logs 
            WHERE username = ? AND logout_time IS NULL 
            ORDER BY login_time DESC LIMIT 1
        ''', (username,))
        result = cursor.fetchone()
        
        if result:
            login_id, login_time = result
            logout_time = datetime.now()
            session_duration = int((logout_time - datetime.fromisoformat(login_time.replace('Z', '+00:00'))).total_seconds())
            
            cursor.execute('''
                UPDATE user_login_logs 
                SET logout_time = ?, session_duration = ?
                WHERE id = ?
            ''', (logout_time.isoformat(), session_duration, login_id))
            return True
        return False
    
    try:
        return safe_db_operation(_log_logout)
    except Exception as e:
        print(f"Error logging user logout: {e}")
        return False

def log_user_activity(username, activity_type, description, bill_number=None):
    """Log user activity"""
    def _log_activity(conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activity_logs (username, activity_type, activity_description, bill_number)
            VALUES (?, ?, ?, ?)
        ''', (username, activity_type, description, bill_number))
        return True
    
    try:
        return safe_db_operation(_log_activity)
    except Exception as e:
        print(f"Error logging user activity: {e}")
        return False

def authenticate_user(username, password):
    """Authenticate user with database"""
    def _authenticate(conn):
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[2], password):
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
        return None
    
    try:
        return safe_db_operation(_authenticate)
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def change_user_password(username, old_password, new_password):
    """Change user password"""
    def _change_password(conn):
        cursor = conn.cursor()
        
        # First verify the old password
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user[0], old_password):
            return False
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ?
        ''', (new_password_hash, username))
        
        return True
    
    try:
        return safe_db_operation(_change_password)
    except Exception as e:
        print(f"Error changing password: {e}")
        return False

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user with database
        user = authenticate_user(username, password)

        # Debug logging
        print(f"Login attempt - Username: {username}, User: {user}")
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            print(f"Login successful - Session: {session}")
            
            # Log user login
            try:
                ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
                user_agent = request.environ.get('HTTP_USER_AGENT')
                log_user_login(user['username'], user['role'], ip_address, user_agent)
            except Exception as e:
                print(f"Error logging user login: {e}")
            
            # Redirect based on role
            if user['role'] == 'admin':
                return jsonify({'success': True, 'redirect_url': url_for('index')})
            else:
                return jsonify({'success': True, 'redirect_url': url_for('user_dashboard')})
        else:
            print(f"Login failed - Username: {username}")
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/test-login', methods=['POST'])
def test_login():
    """Test login endpoint to debug issues"""
    try:
        data = request.get_json()
        print(f"Test login data: {data}")
        return jsonify({'success': True, 'message': 'Test endpoint working', 'data': data})
    except Exception as e:
        print(f"Test login error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/logout')
def logout():
    # Log user logout before clearing session
    if 'username' in session:
        log_user_logout(session['username'])
    
    session.clear()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not old_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New passwords do not match'})
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters long'})
        
        # Change password
        username = session.get('username')
        if change_user_password(username, old_password, new_password):
            # Log password change activity
            log_user_activity(username, 'password_changed', 'User changed their password')
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    return render_template('change_password.html')

@app.route('/user_dashboard')
@user_required
def user_dashboard():
    """User dashboard with limited access"""
    return render_template('user_dashboard.html')

@app.route('/unauthorized')
def unauthorized():
    """Unauthorized access page"""
    return render_template('unauthorized.html')

@app.route('/api/user_dashboard')
@user_required
def api_user_dashboard():
    """API endpoint for user dashboard data"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    
    # Get today's bills count and total revenue
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
        FROM bills 
        WHERE DATE(created_at) = ?
    ''', (today,))
    
    result = cursor.fetchone()
    today_bills = result[0] if result else 0
    total_revenue = result[1] if result else 0
    
    conn.close()
    
    return jsonify({
        'success': True,
        'today_bills': today_bills,
        'total_revenue': total_revenue
    })

@app.route('/')
def root():
    """Root route - redirect to login or dashboard based on authentication"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    elif session.get('role') == 'admin':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/billing')
@login_required
def index():
    """Main billing page"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    
    # Get all categories
    cursor.execute('SELECT DISTINCT category FROM menu ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]
    
    # Get all menu items
    cursor.execute('SELECT * FROM menu ORDER BY category, name')
    menu_items = cursor.fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    items = []
    for item in menu_items:
        items.append({
            'id': item[0],
            'name': item[1],
            'category': item[2],
            'price': item[3],
            'image': item[4],
            'description': item[5]
        })
    
    return render_template('billing.html', categories=categories, menu_items=items)

@app.route('/menu')
@admin_required
def menu_management():
    """Menu management page"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu ORDER BY category, name')
    menu_items = cursor.fetchall()
    conn.close()
    
    items = []
    for item in menu_items:
        items.append({
            'id': item[0],
            'name': item[1],
            'category': item[2],
            'price': item[3],
            'image': item[4],
            'description': item[5]
        })
    
    return render_template('menu.html', menu_items=items)

@app.route('/reports')
@admin_required
def reports():
    """Reports and bills history page"""
    # Get month filter from request
    selected_month = request.args.get('month', '')
    
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    
    # Build query based on month filter
    if selected_month:
        cursor.execute('SELECT * FROM bills WHERE strftime("%Y-%m", created_at) = ? ORDER BY created_at DESC', (selected_month,))
    else:
        cursor.execute('SELECT * FROM bills ORDER BY created_at DESC')
    
    bills = cursor.fetchall()
    conn.close()
    
    bill_list = []
    total_sales = 0
    today_sales = 0
    monthly_sales = 0
    today = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.now().strftime('%Y-%m')
    
    for bill in bills:
        # Parse items JSON string safely
        try:
            items = json.loads(bill[2]) if isinstance(bill[2], str) else bill[2]
            # Ensure items is a list
            if not isinstance(items, list):
                items = []
        except (json.JSONDecodeError, TypeError):
            items = []
            
        bill_data = {
            'id': bill[0],
            'bill_number': bill[1],
            'bill_items': items,  # Renamed from 'items' to 'bill_items' to avoid conflict
            'subtotal': bill[3],
            'tax_amount': bill[4],
            'service_charge': bill[5],
            'total': bill[6],
            'created_at': bill[7]
        }
        bill_list.append(bill_data)
        
        # Calculate totals
        total_sales += bill[6]
        if bill[7].startswith(today):
            today_sales += bill[6]
        if bill[7].startswith(current_month):
            monthly_sales += bill[6]
    
    # Calculate average bill
    avg_bill = total_sales / len(bill_list) if bill_list else 0
    
    # Get available months for dropdown
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT strftime("%Y-%m", created_at) as month FROM bills ORDER BY month DESC')
    available_months = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('reports.html', 
                         bills=bill_list, 
                         total_sales=total_sales,
                         today_sales=today_sales,
                         monthly_sales=monthly_sales,
                         avg_bill=avg_bill,
                         selected_month=selected_month,
                         available_months=available_months)

@app.route('/settings')
@admin_required
def settings():
    """Settings page"""
    settings_data = {
        'tax_rate': get_setting('tax_rate', '10.0'),
        'service_charge_rate': get_setting('service_charge_rate', '5.0'),
        'restaurant_name': get_setting('restaurant_name', 'My Restaurant'),
        'restaurant_address': get_setting('restaurant_address', '123 Main Street, City'),
        'restaurant_phone': get_setting('restaurant_phone', '+1-234-567-8900'),
        'restaurant_gst': get_setting('restaurant_gst', '')
    }
    return render_template('settings.html', settings=settings_data)

@app.route('/api/all_menu_items')
def get_all_menu_items():
    """API endpoint to get all menu items for instant category switching"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu ORDER BY category, name')
    items = cursor.fetchall()
    conn.close()
    
    result = []
    for item in items:
        result.append({
            'id': item[0],
            'name': item[1],
            'category': item[2],
            'price': item[3],
            'image': item[4],
            'description': item[5]
        })
    
    return jsonify(result)

@app.route('/api/menu_items/<category>')
def get_menu_items_by_category(category):
    """API endpoint to get menu items by category"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu WHERE category = ? ORDER BY name', (category,))
    items = cursor.fetchall()
    conn.close()
    
    result = []
    for item in items:
        result.append({
            'id': item[0],
            'name': item[1],
            'category': item[2],
            'price': item[3],
            'image': item[4],
            'description': item[5]
        })
    
    return jsonify(result)

@app.route('/api/add_menu_item', methods=['POST'])
def add_menu_item():
    """API endpoint to add a new menu item"""
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        description = request.form.get('description', '')
        
        # Handle file upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        conn = sqlite3.connect('database/restaurant.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO menu (name, category, price, image, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category, price, image, description))
        conn.commit()
        conn.close()
        
        # Log user activity
        if 'username' in session:
            log_user_activity(
                session['username'], 
                'menu_item_added', 
                f'Added menu item: {name} (₹{price}) in {category} category'
            )
        
        return jsonify({'success': True, 'message': 'Menu item added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/update_menu_item/<int:item_id>', methods=['POST'])
def update_menu_item(item_id):
    """API endpoint to update a menu item"""
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        description = request.form.get('description', '')
        
        conn = sqlite3.connect('database/restaurant.db')
        cursor = conn.cursor()
        
        # Handle file upload if new image provided
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                cursor.execute('''
                    UPDATE menu SET name=?, category=?, price=?, image=?, description=?
                    WHERE id=?
                ''', (name, category, price, filename, description, item_id))
            else:
                cursor.execute('''
                    UPDATE menu SET name=?, category=?, price=?, description=?
                    WHERE id=?
                ''', (name, category, price, description, item_id))
        else:
            cursor.execute('''
                UPDATE menu SET name=?, category=?, price=?, description=?
                WHERE id=?
            ''', (name, category, price, description, item_id))
        
        conn.commit()
        conn.close()
        
        # Log user activity
        if 'username' in session:
            log_user_activity(
                session['username'], 
                'menu_item_updated', 
                f'Updated menu item ID {item_id}: {name} (₹{price}) in {category} category'
            )
        
        return jsonify({'success': True, 'message': 'Menu item updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/delete_menu_item/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    """API endpoint to delete a menu item"""
    try:
        conn = sqlite3.connect('database/restaurant.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM menu WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        
        # Log user activity
        if 'username' in session:
            log_user_activity(
                session['username'], 
                'menu_item_deleted', 
                f'Deleted menu item ID {item_id}'
            )
        
        return jsonify({'success': True, 'message': 'Menu item deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/generate_bill', methods=['POST'])
def generate_bill():
    """API endpoint to generate a bill"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'message': 'No items in bill'})
        
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in items)
        tax_rate = float(get_setting('tax_rate', '10.0'))
        service_charge_rate = float(get_setting('service_charge_rate', '5.0'))
        
        tax_amount = (subtotal * tax_rate) / 100
        service_charge = (subtotal * service_charge_rate) / 100
        total = subtotal + tax_amount + service_charge
        
        # Generate bill number in new format: A/F/E + DD-MM-YYYY + / + sequence
        current_time = datetime.now()
        current_hour = current_time.hour
        today = date.today()
        
        # Determine prefix by time of day
        # A: 00:00 - 12:59 (till 1 PM)
        # F: 13:00 - 17:59 (1 PM to 6 PM)
        # E: 18:00 - 23:59 (after 6 PM)
        if current_hour < 13:
            prefix = "A"
        elif current_hour < 18:
            prefix = "F"
        else:
            prefix = "E"
        
        # Format date as DD-MM-YYYY
        date_str = today.strftime('%d-%m-%Y')
        
        # Get or create daily sequence number
        conn = sqlite3.connect('database/restaurant.db')
        cursor = conn.cursor()
        today_str = today.strftime('%Y-%m-%d')
        cursor.execute('SELECT last_seq FROM daily_sequence WHERE seq_date = ?', (today_str,))
        row = cursor.fetchone()
        last_seq = row[0] if row else 0
        next_seq = (last_seq + 1) if last_seq else 1
        
        # Update sequence number
        if row:
            cursor.execute('UPDATE daily_sequence SET last_seq = ? WHERE seq_date = ?', (next_seq, today_str))
        else:
            cursor.execute('INSERT INTO daily_sequence (seq_date, last_seq) VALUES (?, ?)', (today_str, next_seq))
        
        # Create bill number in format: A/F/E + DD-MM-YYYY + / + sequence
        # Examples: A15-12-2024/001, F15-12-2024/002, E15-12-2024/003
        bill_number = f"{prefix}{date_str}/{next_seq:03d}"
        
        # Save to database
        cursor.execute('''
            INSERT INTO bills (bill_number, items, subtotal, tax_amount, service_charge, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bill_number, json.dumps(items), subtotal, tax_amount, service_charge, total))

        # Save bill's daily sequence mapping
        cursor.execute('INSERT OR REPLACE INTO bill_sequence (bill_number, seq_date, seq_number) VALUES (?, ?, ?)', (bill_number, today_str, next_seq))
        conn.commit()
        conn.close()
        
        # Log user activity for bill generation
        if 'username' in session:
            log_user_activity(
                session['username'], 
                'bill_generated', 
                f'Generated bill {bill_number} with {len(items)} items, total: ₹{total:.2f}',
                bill_number
            )
        
        return jsonify({
            'success': True,
            'bill_number': bill_number,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'service_charge': service_charge,
            'total': total
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    """API endpoint to update settings"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            set_setting(key, value)
        
        # Log user activity
        if 'username' in session:
            log_user_activity(
                session['username'], 
                'settings_updated', 
                f'Updated settings: {", ".join(data.keys())}'
            )
        
        return jsonify({'success': True, 'message': 'Settings updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/settings')
def get_settings():
    """API endpoint to get all settings"""
    try:
        settings_data = {
            'tax_rate': get_setting('tax_rate', '10.0'),
            'service_charge_rate': get_setting('service_charge_rate', '5.0'),
            'restaurant_name': get_setting('restaurant_name', 'My Restaurant'),
            'restaurant_address': get_setting('restaurant_address', '123 Main Street, City'),
            'restaurant_phone': get_setting('restaurant_phone', '+1-234-567-8900'),
            'restaurant_gst': get_setting('restaurant_gst', '')
        }
        return jsonify(settings_data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/bill/<path:bill_number>')
def view_bill(bill_number):
    """View printable bill"""
    def _get_bill(conn):
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bills WHERE bill_number = ?', (bill_number,))
        bill = cursor.fetchone()
        
        # Fetch sequence number if available
        seq_number = None
        try:
            cursor.execute('SELECT seq_number FROM bill_sequence WHERE bill_number = ?', (bill_number,))
            row = cursor.fetchone()
            if row:
                seq_number = row[0]
        except sqlite3.OperationalError:
            seq_number = None
        
        return bill, seq_number
    
    try:
        bill, seq_number = safe_db_operation(_get_bill)
    except Exception as e:
        print(f"Error fetching bill {bill_number}: {e}")
        flash('Error loading bill', 'error')
        return redirect(url_for('reports'))
    
    if not bill:
        flash('Bill not found', 'error')
        return redirect(url_for('reports'))
    
    # Parse items JSON string
    try:
        items = json.loads(bill[2]) if isinstance(bill[2], str) else bill[2]
        # Ensure items is a list
        if not isinstance(items, list):
            items = []
    except (json.JSONDecodeError, TypeError):
        items = []
    
    bill_data = {
        'id': bill[0],
        'bill_number': bill[1],
        'bill_items': items,  # Renamed from 'items' to 'bill_items' to avoid conflict
        'subtotal': bill[3],
        'tax_amount': bill[4],
        'service_charge': bill[5],
        'total': bill[6],
        'created_at': bill[7],
        'seq_number': seq_number
    }
    
    # Get restaurant settings
    settings_data = {
        'restaurant_name': get_setting('restaurant_name', 'My Restaurant'),
        'restaurant_address': get_setting('restaurant_address', '123 Main Street, City'),
        'restaurant_phone': get_setting('restaurant_phone', '+1-234-567-8900'),
        'restaurant_gst': get_setting('restaurant_gst', '')
    }
    
    copy_type = request.args.get('copy', 'student')
    return render_template('bill_print.html', bill=bill_data, settings=settings_data, copy_type=copy_type)

@app.route('/api/user_logs')
@admin_required
def get_user_logs():
    """API endpoint to get user login and activity logs"""
    try:
        conn = sqlite3.connect('database/restaurant.db')
        cursor = conn.cursor()
        
        # Get login logs
        cursor.execute('''
            SELECT username, role, login_time, logout_time, session_duration, ip_address
            FROM user_login_logs 
            ORDER BY login_time DESC 
            LIMIT 100
        ''')
        login_logs = []
        for row in cursor.fetchall():
            login_logs.append({
                'username': row[0],
                'role': row[1],
                'login_time': row[2],
                'logout_time': row[3],
                'session_duration': row[4],
                'ip_address': row[5]
            })
        
        # Get activity logs
        cursor.execute('''
            SELECT username, activity_type, activity_description, bill_number, created_at
            FROM user_activity_logs 
            ORDER BY created_at DESC 
            LIMIT 100
        ''')
        activity_logs = []
        for row in cursor.fetchall():
            activity_logs.append({
                'username': row[0],
                'activity_type': row[1],
                'activity_description': row[2],
                'bill_number': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'login_logs': login_logs,
            'activity_logs': activity_logs
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/check_database')
@admin_required
def check_database():
    """API endpoint to check and fix database issues"""
    try:
        if check_and_fix_database():
            return jsonify({'success': True, 'message': 'Database is accessible and working properly'})
        else:
            return jsonify({'success': False, 'message': 'Database has issues that could not be automatically fixed'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database check failed: {str(e)}'})

@app.route('/api/delete_bill/<path:bill_number>', methods=['DELETE'])
@admin_required
def delete_bill(bill_number):
    """API endpoint to delete a bill (admin only)"""
    try:
        def _delete_bill(conn):
            cursor = conn.cursor()
            
            # First check if bill exists
            cursor.execute('SELECT id, total FROM bills WHERE bill_number = ?', (bill_number,))
            bill = cursor.fetchone()
            
            if not bill:
                return False, "Bill not found"
            
            bill_id, bill_total = bill
            
            # Delete the bill
            cursor.execute('DELETE FROM bills WHERE bill_number = ?', (bill_number,))
            
            # Also delete from bill_sequence table if it exists
            try:
                cursor.execute('DELETE FROM bill_sequence WHERE bill_number = ?', (bill_number,))
            except sqlite3.OperationalError:
                # Table might not exist in older versions, ignore
                pass
            
            return True, f"Bill {bill_number} deleted successfully"
        
        success, message = safe_db_operation(_delete_bill)
        
        if success:
            # Log the deletion activity
            if 'username' in session:
                log_user_activity(
                    session['username'], 
                    'bill_deleted', 
                    f'Deleted bill {bill_number}',
                    bill_number
                )
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
            
    except Exception as e:
        print(f"Error deleting bill {bill_number}: {e}")
        return jsonify({'success': False, 'message': f'Error deleting bill: {str(e)}'})


@app.route('/api/item_analysis')
@admin_required
def get_item_analysis():
    """API endpoint to get item analysis for the selected date range"""
    try:
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on date range
        if from_date and to_date:
            cursor.execute('''
                SELECT bill_items, total, created_at 
                FROM bills 
                WHERE DATE(created_at) BETWEEN ? AND ? 
                ORDER BY created_at DESC
            ''', (from_date, to_date))
        elif from_date:
            cursor.execute('''
                SELECT bill_items, total, created_at 
                FROM bills 
                WHERE DATE(created_at) >= ? 
                ORDER BY created_at DESC
            ''', (from_date,))
        elif to_date:
            cursor.execute('''
                SELECT bill_items, total, created_at 
                FROM bills 
                WHERE DATE(created_at) <= ? 
                ORDER BY created_at DESC
            ''', (to_date,))
        else:
            cursor.execute('''
                SELECT bill_items, total, created_at 
                FROM bills 
                ORDER BY created_at DESC
            ''')
        
        bills = cursor.fetchall()
        conn.close()
        
        # Analyze items
        item_analysis = {}
        total_sales = 0
        
        for bill in bills:
            try:
                items = json.loads(bill[0]) if isinstance(bill[0], str) else bill[0]
                bill_total = bill[1]
                total_sales += bill_total
                
                if isinstance(items, list):
                    for item in items:
                        item_name = item.get('name', 'Unknown')
                        quantity = item.get('quantity', 0)
                        price = item.get('price', 0)
                        item_total = price * quantity
                        
                        if item_name in item_analysis:
                            item_analysis[item_name]['quantity'] += quantity
                            item_analysis[item_name]['total_sales'] += item_total
                        else:
                            item_analysis[item_name] = {
                                'quantity': quantity,
                                'price': price,
                                'total_sales': item_total
                            }
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
        
        # Sort by total sales (highest first)
        sorted_items = sorted(
            item_analysis.items(), 
            key=lambda x: x[1]['total_sales'], 
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'item_analysis': [{
                'name': name,
                'quantity': data['quantity'],
                'price': data['price'],
                'total_sales': data['total_sales']
            } for name, data in sorted_items],
            'total_sales': total_sales,
            'total_bills': len(bills)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test_bill_number')
@admin_required
def test_bill_number():
    """Test endpoint to generate a sample bill number"""
    try:
        current_time = datetime.now()
        current_hour = current_time.hour
        today = date.today()
        
        # Determine prefix: F for morning (before 10 AM), A for afternoon/evening
        prefix = "F" if current_hour < 10 else "A"
        
        # Format date as DD-MM-YYYY
        date_str = today.strftime('%d-%m-%Y')
        
        # Get current sequence
        def _get_sequence(conn):
            cursor = conn.cursor()
            today_str = today.strftime('%Y-%m-%d')
            cursor.execute('SELECT last_seq FROM daily_sequence WHERE seq_date = ?', (today_str,))
            row = cursor.fetchone()
            last_seq = row[0] if row else 0
            next_seq = (last_seq + 1) if last_seq else 1
            return next_seq
        
        next_seq = safe_db_operation(_get_sequence)
        
        # Create sample bill number
        sample_bill_number = f"{prefix}{date_str}/{next_seq:03d}"
        
        return jsonify({
            'success': True,
            'sample_bill_number': sample_bill_number,
            'prefix': prefix,
            'date_str': date_str,
            'next_seq': next_seq,
            'current_hour': current_hour
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
