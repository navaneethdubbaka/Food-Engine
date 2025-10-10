# 🍽️ Restaurant Billing System

A clean, fast, offline Flask-based billing system for restaurants that allows staff to select food items, generate bills, manage menu items, and view sales reports.

## ✨ Features

### 🧾 Billing System
- **Category-based menu selection** - Choose from starters, main course, desserts, etc.
- **Visual menu cards** - Items displayed with images and prices
- **Real-time bill calculation** - Automatic subtotal, tax, and service charge calculation
- **Printable bills** - Generate professional receipts
- **Bill management** - Add/remove items, adjust quantities

### 🍴 Menu Management
- **Add/Edit/Delete items** - Full CRUD operations for menu items
- **Category organization** - Organize items by food categories
- **Image uploads** - Upload food images for better presentation
- **Price management** - Set and update item prices
- **Description support** - Add detailed item descriptions

### ⚙️ Settings & Configuration
- **Tax rate configuration** - Set custom tax percentages
- **Service charge settings** - Configure service charges
- **Restaurant information** - Set restaurant name, address, phone
- **System preferences** - Customize billing behavior

### 📊 Reports & Analytics
- **Sales history** - View all generated bills
- **Date filtering** - Filter bills by date range
- **Sales summary** - Total sales, average bill amount
- **CSV export** - Export data for external analysis
- **Bill search** - Find specific bills quickly

### 🎨 Modern UI
- **Bootstrap 5 design** - Clean, responsive interface
- **Warm orange theme** - Food-friendly color scheme
- **Mobile responsive** - Works on tablets and phones
- **Offline components** - No internet required

## 🚀 Quick Start

### Option 1: Run as Python Application

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   - Go to `http://localhost:5000`
   - The system will automatically create the database

### Option 2: Create Executable (Windows)

1. **Build executable:**
   ```bash
   python build_exe.py
   ```

2. **Distribute:**
   - Find the `RestaurantBilling_Distribution` folder
   - Zip and share with users
   - Users can run `RestaurantBilling.exe` directly

## 📁 Project Structure

```
restaurant_billing/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── build_exe.py             # Build script for executable
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── billing.html        # Main billing interface
│   ├── menu.html           # Menu management
│   ├── reports.html        # Sales reports
│   ├── settings.html       # System settings
│   └── bill_print.html     # Printable bill template
├── static/                 # Static assets
│   ├── css/
│   │   ├── style.css       # Custom styles
│   │   └── bootstrap.min.css # Bootstrap 5 (offline)
│   ├── js/
│   │   ├── main.js         # Main JavaScript
│   │   └── bootstrap.bundle.min.js # Bootstrap JS (offline)
│   └── images/             # Uploaded food images
├── database/               # SQLite database
│   └── restaurant.db       # Main database file
└── utils/                  # Utility functions
```

## 🗄️ Database Schema

### Menu Table
- `id` - Primary key
- `name` - Item name
- `category` - Food category
- `price` - Item price
- `image` - Image filename
- `description` - Item description
- `created_at` - Creation timestamp

### Bills Table
- `id` - Primary key
- `bill_number` - Unique bill identifier
- `items` - JSON array of bill items
- `subtotal` - Pre-tax amount
- `tax_amount` - Tax amount
- `service_charge` - Service charge amount
- `total` - Final total
- `created_at` - Creation timestamp

### Settings Table
- `id` - Primary key
- `key` - Setting name
- `value` - Setting value
- `updated_at` - Last update timestamp

## 🎯 Usage Guide

### First Time Setup

1. **Configure Settings:**
   - Go to Settings page
   - Set restaurant name, address, phone
   - Configure tax rate and service charge
   - Save settings

2. **Add Menu Items:**
   - Go to Menu page
   - Click "Add Menu Item"
   - Fill in item details (name, category, price)
   - Upload food image (optional)
   - Save item

3. **Start Billing:**
   - Go to Billing page
   - Select a category
   - Click items to add to bill
   - Adjust quantities as needed
   - Generate bill when ready

### Daily Operations

1. **Create Bills:**
   - Select category from chips
   - Click food items to add to bill
   - Use quantity controls to adjust amounts
   - Click "Generate Bill" to create receipt

2. **View Reports:**
   - Go to Reports page
   - Filter by date range
   - Search for specific bills
   - Export data as CSV

3. **Manage Menu:**
   - Add new items as needed
   - Update prices
   - Remove discontinued items
   - Organize by categories

## 🔧 Configuration

### Tax and Service Charge
- Set tax rate (default: 10%)
- Set service charge rate (default: 5%)
- Both are applied to subtotal

### Restaurant Information
- Restaurant name (appears on bills)
- Address (appears on bills)
- Phone number (appears on bills)

### Categories
Default categories include:
- Starters
- Main Course
- Desserts
- Beverages
- Appetizers
- Salads
- Soups
- Pizza
- Pasta
- Burgers
- Sandwiches
- Other

## 📱 Mobile Support

The system is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Touch screen devices

## 🔒 Data Security

- **Local storage only** - All data stays on your computer
- **No internet required** - Completely offline operation
- **SQLite database** - Reliable, file-based storage
- **No cloud dependencies** - Your data never leaves your system

## 🛠️ Technical Details

### Built With
- **Flask** - Python web framework
- **SQLite** - Local database
- **Bootstrap 5** - UI framework (offline)
- **JavaScript** - Interactive features
- **PyInstaller** - Executable creation

### System Requirements
- **Python 3.7+** (for development)
- **Windows 10+** (for executable)
- **No internet connection required**
- **No additional software needed**

## 🚀 Deployment Options

### 1. Python Development
- Install Python and dependencies
- Run `python app.py`
- Access via web browser

### 2. Executable Distribution
- Run `python build_exe.py`
- Distribute the generated folder
- Users run `RestaurantBilling.exe`

### 3. Network Deployment
- Run on server computer
- Access from multiple terminals
- Share database across devices

## 📞 Support

This is a standalone application designed for:
- Small to medium restaurants
- Food trucks
- Cafes and coffee shops
- Any business needing simple billing

## 🔄 Updates

To update the system:
1. Backup your database folder
2. Replace application files
3. Restore database folder
4. All your data will be preserved

## 📄 License

This project is open source and available under the MIT License.

---

**Ready to get started?** Run `python app.py` and open `http://localhost:5000` in your browser!
