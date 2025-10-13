from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, session
import sqlite3
import os
from datetime import datetime, date
import json
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'restaurant_billing_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('database', exist_ok=True)

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
    
    # Insert default settings if not exists
    default_settings = [
        ('tax_rate', '10.0'),
        ('service_charge_rate', '5.0'),
        ('restaurant_name', 'My Restaurant'),
        ('restaurant_address', '123 Main Street, City'),
        ('restaurant_phone', '+1-234-567-8900')
    ]
    
    for key, value in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
    
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """Get a setting value from database"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

def set_setting(key, value):
    """Set a setting value in database"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', (key, value))
    conn.commit()
    conn.close()

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Simple authentication (in production, use proper password hashing)
        if role == 'admin' and username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = 'admin'
            session['role'] = 'admin'
            return jsonify({'success': True, 'redirect_url': url_for('index')})
        elif role == 'user' and username == 'user' and password == 'user123':
            session['user_id'] = 2
            session['username'] = 'user'
            session['role'] = 'user'
            return jsonify({'success': True, 'redirect_url': url_for('user_dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
        'restaurant_phone': get_setting('restaurant_phone', '+1-234-567-8900')
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
        
        # Generate bill number
        bill_number = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save to database
        conn = sqlite3.connect('database/restaurant.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bills (bill_number, items, subtotal, tax_amount, service_charge, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bill_number, json.dumps(items), subtotal, tax_amount, service_charge, total))
        conn.commit()
        conn.close()
        
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
            'restaurant_phone': get_setting('restaurant_phone', '+1-234-567-8900')
        }
        return jsonify(settings_data)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/bill/<bill_number>')
def view_bill(bill_number):
    """View printable bill"""
    conn = sqlite3.connect('database/restaurant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bills WHERE bill_number = ?', (bill_number,))
    bill = cursor.fetchone()
    conn.close()
    
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
        'created_at': bill[7]
    }
    
    # Get restaurant settings
    settings_data = {
        'restaurant_name': get_setting('restaurant_name', 'My Restaurant'),
        'restaurant_address': get_setting('restaurant_address', '123 Main Street, City'),
        'restaurant_phone': get_setting('restaurant_phone', '+1-234-567-8900')
    }
    
    return render_template('bill_print.html', bill=bill_data, settings=settings_data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
