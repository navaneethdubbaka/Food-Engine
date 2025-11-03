"""
Script to update menu items in the database from JSON data.
This script will:
1. Compare JSON menu data with existing database items
2. Update names and prices for existing items
3. Add new items that don't exist
4. Ensure all categories exist in the database
"""

import sqlite3
import json
from datetime import datetime

# JSON menu data
MENU_DATA = {
  "break_fast": [
    {"item": "IDLY", "price": 40},
    {"item": "VADA", "price": 30},
    {"item": "IDLY (2) + BONDA (1)", "price": 50},
    {"item": "VADA (2) + IDLY (1)", "price": 50},
    {"item": "MYSORE BONDA", "price": 40},
    {"item": "SAMBAR IDLY", "price": 50},
    {"item": "UPMA", "price": 40},
    {"item": "ONION DOSA", "price": 60},
    {"item": "ONION UTTAPAM", "price": 60},
    {"item": "PLAIN DOSA", "price": 50},
    {"item": "GHEE KARAM DOSA", "price": 60},
    {"item": "PANEER DOSA", "price": 80},
    {"item": "MASALA DOSA", "price": 70},
    {"item": "RAVA DOSA", "price": 70},
    {"item": "RAVA MASALA DOSA", "price": 80},
    {"item": "GHEE DOSA", "price": 60},
    {"item": "CHEESE DOSA", "price": 80},
    {"item": "OMLET", "price": 40},
    {"item": "BOILED EGG", "price": 10}
  ],
  "continental_veg": [
    {"item": "FRENCH FRIES", "price": 100},
    {"item": "PERI PERI FRIES", "price": 110},
    {"item": "YUMMY CHEESE FRIES", "price": 140},
    {"item": "VEG ROLL", "price": 80},
    {"item": "VEG PAPAD", "price": 40},
    {"item": "VEG MAGGI", "price": 70},
    {"item": "PANEER ROLL", "price": 140}
  ],
  "continental_non_veg": [
    {"item": "CHICKEN ROLL", "price": 140},
    {"item": "CHICKEN CHEESE FRIES", "price": 160},
    {"item": "CHICKEN POPCORN", "price": 140},
    {"item": "CHICKEN NUGGETS", "price": 130}
  ],
  "burgers": [
    {"item": "VEG BURGER", "price": 80},
    {"item": "CHEESE BURGER", "price": 130},
    {"item": "CHEESE PANEER BURGER", "price": 140},
    {"item": "CHEESE TIKKA BURGER", "price": 140}
  ],
  "sandwich": [
    {"item": "VEG SANDWICH", "price": 120},
    {"item": "CHEESE SANDWICH", "price": 140},
    {"item": "CHICKEN SANDWICH", "price": 140},
    {"item": "EGG SANDWICH", "price": 120}
  ],
  "pasta_pizza": [
    {"item": "VEG PASTA", "price": 150},
    {"item": "CHICKEN PASTA", "price": 180},
    {"item": "PANEER PASTA", "price": 160},
    {"item": "MIX PASTA", "price": 170},
    {"item": "CORN PIZZA", "price": 150},
    {"item": "CHEESE VEG PIZZA", "price": 150},
    {"item": "PANEER PIZZA", "price": 180},
    {"item": "CHICKEN CHEESE PIZZA", "price": 180},
    {"item": "CHICKEN PIZZA", "price": 180},
    {"item": "CHICKEN TIKKA PIZZA", "price": 180},
    {"item": "CHICKEN CORN PIZZA", "price": 180}
  ],
  "soups_veg": [
    {"item": "TOMATO SOUP", "price": 60},
    {"item": "SWEET CORN SOUP", "price": 80},
    {"item": "MANCHOW SOUP", "price": 100},
    {"item": "HOT & SOUR SOUP", "price": 100}
  ],
  "soups_non_veg": [
    {"item": "CHICKEN SWEET CORN", "price": 120},
    {"item": "CHICKEN MANCHOW", "price": 120},
    {"item": "CHICKEN HOT & SOUR", "price": 120}
  ],
  "starters_veg": [
    {"item": "VEG MANCHURIA", "price": 100},
    {"item": "MUSHROOM 65", "price": 120},
    {"item": "PANEER 65", "price": 120},
    {"item": "BABY CORN MANCHURIA", "price": 120},
    {"item": "CRISPY BABY CORN", "price": 140},
    {"item": "GOBI 65", "price": 100},
    {"item": "MUSHROOM 65", "price": 120},
    {"item": "CHILLI GOBI", "price": 120},
    {"item": "CHILLI BABY CORN", "price": 140},
    {"item": "VEG MAJESTIC", "price": 150}
  ],
  "starters_non_veg": [
    {"item": "EGG MANCHURIA", "price": 80},
    {"item": "CHICKEN MANCHURIA", "price": 140},
    {"item": "PRAWN MANCHURIA", "price": 180},
    {"item": "APOLLO FISH", "price": 180},
    {"item": "CRISPY CHICKEN", "price": 180},
    {"item": "CHICKEN 65", "price": 130},
    {"item": "CHILLI CHICKEN", "price": 150},
    {"item": "SCHEZWAN CHICKEN", "price": 150},
    {"item": "CHICKEN 555", "price": 150},
    {"item": "CHICKEN MAJESTIC", "price": 150},
    {"item": "FISH 65", "price": 150},
    {"item": "PRAWN 65", "price": 180},
    {"item": "CHICKEN PAKODA BONELESS", "price": 180}
  ],
  "fried_rice_veg": [
    {"item": "VEG FRIED RICE", "price": 100},
    {"item": "VEG SCHEZWAN FRIED RICE", "price": 110},
    {"item": "CASHEW VEG FRIED RICE", "price": 150},
    {"item": "VEG MANCHURIAN FRIED RICE", "price": 120},
    {"item": "PANEER FRIED RICE", "price": 120},
    {"item": "PANEER SEZWAN FRIED RICE", "price": 130},
    {"item": "CHILLI PANEER FRIED RICE", "price": 140},
    {"item": "MUSHROOM FRIED RICE", "price": 130},
    {"item": "MUSHROOM SEZWAN FRIED RICE", "price": 150},
    {"item": "MUSHROOM MANCHURIAN FRIED RICE", "price": 150},
    {"item": "CHILLI MUSHROOM FRIED RICE", "price": 170}
  ],
  "fried_rice_non_veg": [
    {"item": "EGG FRIED RICE", "price": 120},
    {"item": "EGG SEZWAN FRIED RICE", "price": 130},
    {"item": "CHICKEN FRIED RICE", "price": 130},
    {"item": "CHICKEN SCHEZWAN FRIED RICE", "price": 150},
    {"item": "CHILLI CHICKEN FRIED RICE", "price": 150},
    {"item": "CHICKEN MANCHURIAN FRIED RICE", "price": 150},
    {"item": "CHICKEN 65 FRIED RICE", "price": 170},
    {"item": "MIX NON VEG FRIED RICE", "price": 200},
    {"item": "SPECIAL CHICKEN FRIED RICE", "price": 180},
    {"item": "PRAWN FRIED RICE", "price": 220}
  ],
  "biryanis_veg": [
    {"item": "VEG BIRYANI", "price": 100},
    {"item": "PANEER BIRYANI", "price": 150},
    {"item": "MUSHROOM BIRYANI", "price": 150}
  ],
  "biryanis_non_veg": [
    {"item": "EGG BIRYANI", "price": 150},
    {"item": "SINGLE PIECE BIRYANI", "price": 180},
    {"item": "CHICKEN DUM BIRYANI", "price": 200},
    {"item": "CHICKEN FRY BONE/BONELESS BIRYANI", "price_bone": 200, "price_boneless": 220},
    {"item": "SPL CHICKEN BIRYANI", "price": 200},
    {"item": "CHICKEN MUGHLAI BONE/BONELESS", "price_bone": 200, "price_boneless": 220},
    {"item": "LOLLIPOP BIRYANI", "price": 200},
    {"item": "CHICKEN TIKKA BIRYANI", "price": 200},
    {"item": "KALMI BIRYANI", "price": 210},
    {"item": "BUTTER CHICKEN BIRYANI", "price": 220},
    {"item": "PRAWN BIRYANI", "price": 220},
    {"item": "FISH BIRYANI", "price": 200},
    {"item": "MIXED BIRYANI", "price": 180}
  ],
  "tandoori_veg": [
    {"item": "PANEER TIKKA", "price": 200},
    {"item": "PANEER MALAI TIKKA", "price": 220}
  ],
  "tandoori_non_veg": [
    {"item": "MURGH MALAI KABAB", "price": 220},
    {"item": "KALMI KABAB", "price": 280},
    {"item": "CHICKEN TIKKA", "price": 250},
    {"item": "CHICKEN TANDOORI (HALF)", "price": 250},
    {"item": "CHICKEN TANDOORI (FULL)", "price": 450}
  ],
  "noodles_veg": [
    {"item": "VEG NOODLES", "price": 100},
    {"item": "EGG NOODLES", "price": 120},
    {"item": "PANEER NOODLES", "price": 140},
    {"item": "CHILLI PANEER NOODLES", "price": 150},
    {"item": "CHILLI MUSHROOM NOODLES", "price": 170}
  ],
  "noodles_non_veg": [
    {"item": "EGG NOODLES", "price": 120},
    {"item": "CHICKEN NOODLES", "price": 130},
    {"item": "CHICKEN SCHEZWAN NOODLES", "price": 150},
    {"item": "CHICKEN MANCHURIAN NOODLES", "price": 150}
  ],
  "curries_veg": [
    {"item": "MIXED VEG", "price": 140},
    {"item": "KADI VEG", "price": 140},
    {"item": "PANEER BUTTER MASALA", "price": 150},
    {"item": "PANEER MASALA", "price": 150},
    {"item": "KADAI PANEER", "price": 170},
    {"item": "METHI PANEER", "price": 150},
    {"item": "SHYANA PANEER", "price": 150},
    {"item": "MUSHROOM MASALA", "price": 150},
    {"item": "MUSHROOM PANEER MASALA", "price": 170},
    {"item": "METHI MUSHROOM", "price": 170},
    {"item": "KASHMIRI MUSHROOM", "price": 170},
    {"item": "CHEESE TOMATO", "price": 120},
    {"item": "VEG KOLHAPURI", "price": 150}
  ],
  "curries_non_veg": [
    {"item": "BUTTER CHICKEN", "price_bone": 180, "price_boneless": 200},
    {"item": "CHICKEN CURRY", "price_bone": 150, "price_boneless": 180},
    {"item": "CHICKEN TIKKA MASALA", "price": 200},
    {"item": "CHICKEN CHATPATA", "price": 180},
    {"item": "CHICKEN MASALA", "price": 180},
    {"item": "CHICKEN KOLHAPURI", "price": 180},
    {"item": "CHICKEN THENTHINDU", "price": 180},
    {"item": "MUSHROOM CHICKEN CURRY", "price": 200},
    {"item": "EGG CURRY/FRY", "price": 70},
    {"item": "BUTTER PRAWN MASALA", "price": 180}
  ],
  "breads": [
    {"item": "BUTTER NAAN", "price": 40},
    {"item": "PLAIN NAAN", "price": 30},
    {"item": "GARLIC NAAN", "price": 50},
    {"item": "TANDOOR ROTI", "price": 30},
    {"item": "PULKA", "price": 10},
    {"item": "BUTTER PULKA", "price": 15}
  ],
  "meals": [
    {"item": "VEG MEALS", "price": 80},
    {"item": "FULL MEALS", "price": 100},
    {"item": "BACHELOR'S MEALS", "price": 70},
    {"item": "EGG MEALS", "price": 100},
    {"item": "CHICKEN MEALS", "price": 180},
    {"item": "CURD RICE", "price": 70},
    {"item": "PULI SADHAM", "price": 70},
    {"item": "DAL RICE", "price": 70},
    {"item": "EGG RICE", "price": 80},
    {"item": "PAAL RICE", "price": 70}
  ],
  "beverages": [
    {"item": "TEA", "price": 10},
    {"item": "COFFEE", "price": 15},
    {"item": "BOOST/HORLICKS", "price": 20},
    {"item": "BUTTER MILK", "price": 15},
    {"item": "SWEET LASSI", "price": 20},
    {"item": "WAFFLE", "price": 70},
    {"item": "GULAB JAMUN (ICECREAM)", "price": 40}
  ]
}


def format_category_name(category_key):
    """Convert category key (with underscores) to display name"""
    # Replace underscores with spaces and title case
    return category_key.replace('_', ' ').title()

def normalize_category_name(category_name):
    """Normalize category name to match JSON format"""
    # Remove spaces around parentheses and normalize
    normalized = category_name.strip()
    
    # Map variations to canonical format from JSON
    category_mapping = {
        # Exact matches first
        'Break Fast': 'Break Fast',
        'Breakfast': 'Break Fast',
        'Continental Veg': 'Continental Veg',
        'Continental (Veg)': 'Continental Veg',
        'Continental Non Veg': 'Continental Non Veg',
        'Continental (Non-Veg)': 'Continental Non Veg',
        'Biryanis Veg': 'Biryanis Veg',
        'Biryanis (Veg)': 'Biryanis Veg',
        'Biryanis Non Veg': 'Biryanis Non Veg',
        'Biryanis (Non-Veg)': 'Biryanis Non Veg',
        'Curries Veg': 'Curries Veg',
        'Curries (Veg)': 'Curries Veg',
        'Curries Non Veg': 'Curries Non Veg',
        'Curries (Non-Veg)': 'Curries Non Veg',
        'Fried Rice Veg': 'Fried Rice Veg',
        'Fried Rice (Veg)': 'Fried Rice Veg',
        'Fried Rice Non Veg': 'Fried Rice Non Veg',
        'Fried Rice (Non-Veg)': 'Fried Rice Non Veg',
        'Noodles Veg': 'Noodles Veg',
        'Noodles (Veg)': 'Noodles Veg',
        'Noodles Non Veg': 'Noodles Non Veg',
        'Noodles (Non-Veg)': 'Noodles Non Veg',
        'Soups Veg': 'Soups Veg',
        'Soups (Veg)': 'Soups Veg',
        'Soups Non Veg': 'Soups Non Veg',
        'Soups (Non-Veg)': 'Soups Non Veg',
        'Starters Veg': 'Starters Veg',
        'Starters (Veg)': 'Starters Veg',
        'Starters Non Veg': 'Starters Non Veg',
        'Starters (Non-Veg)': 'Starters Non Veg',
        'Tandoori Veg': 'Tandoori Veg',
        'Tandoori (Veg)': 'Tandoori Veg',
        'Tandoori Non Veg': 'Tandoori Non Veg',
        'Tandoori (Non-Veg)': 'Tandoori Non Veg',
        'Pasta Pizza': 'Pasta Pizza',
        'Pasta': 'Pasta Pizza',
        'Pizza': 'Pasta Pizza',
    }
    
    # Try exact match first
    if normalized in category_mapping:
        return category_mapping[normalized]
    
    # Try case-insensitive match
    normalized_upper = normalized.upper()
    for key, mapped_value in category_mapping.items():
        if key.upper() == normalized_upper:
            return mapped_value
    
    # Remove spaces around parentheses
    normalized = normalized.replace(' (', '(').replace('( ', '(').replace(' )', ')').replace(') ', ')')
    
    # Try again with cleaned name
    if normalized in category_mapping:
        return category_mapping[normalized]
    
    # Return original if no mapping found
    return normalized

def cleanup_category_duplicates():
    """Merge duplicate categories and update items to use canonical category names"""
    db_path = 'database/restaurant.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("CLEANING UP DUPLICATE CATEGORIES")
        print("=" * 60)
        print()
        
        # Get all unique categories
        cursor.execute('SELECT DISTINCT category FROM menu ORDER BY category')
        all_categories = [row[0] for row in cursor.fetchall()]
        
        # Group categories by normalized name
        category_groups = {}
        for category in all_categories:
            normalized = normalize_category_name(category)
            if normalized not in category_groups:
                category_groups[normalized] = []
            category_groups[normalized].append(category)
        
        # Find duplicate groups (categories that normalize to the same name)
        duplicates_found = 0
        items_moved = 0
        categories_deleted = 0
        
        for canonical_category, category_variants in category_groups.items():
            if len(category_variants) > 1:
                duplicates_found += 1
                print(f"\nDuplicate categories found for: '{canonical_category}'")
                print(f"  Variants: {', '.join(category_variants)}")
                
                # Choose the canonical category (prefer the one matching JSON format)
                # Check which variant matches the JSON format exactly
                canonical_variant = None
                for variant in category_variants:
                    if variant == canonical_category:
                        canonical_variant = variant
                        break
                
                # If no exact match, prefer the one closest to JSON format
                if not canonical_variant:
                    # Prefer variants without parentheses, then shorter names
                    category_variants_sorted = sorted(category_variants, 
                                                      key=lambda x: (
                                                          '(' in x,  # False (no parentheses) comes first
                                                          len(x),    # Shorter names preferred
                                                          x          # Alphabetical tiebreaker
                                                      ))
                    canonical_variant = category_variants_sorted[0]
                
                # But always use the canonical category name from JSON (not the variant)
                # This ensures consistency with JSON format
                canonical_variant = canonical_category
                
                print(f"  Using canonical: '{canonical_variant}'")
                
                # Update all items from duplicate categories to use canonical category
                for variant in category_variants:
                    if variant != canonical_variant:
                        # Get count of items in this variant
                        cursor.execute('SELECT COUNT(*) FROM menu WHERE category = ?', (variant,))
                        count = cursor.fetchone()[0]
                        
                        if count > 0:
                            # Update items to use canonical category
                            cursor.execute(
                                'UPDATE menu SET category = ? WHERE category = ?',
                                (canonical_variant, variant)
                            )
                            items_moved += count
                            print(f"  Moved {count} items from '{variant}' to '{canonical_variant}'")
                        
                        # Check if category is now empty
                        cursor.execute('SELECT COUNT(*) FROM menu WHERE category = ?', (variant,))
                        if cursor.fetchone()[0] == 0:
                            # Category is empty (all items moved), but we can't delete it
                            # because categories are just strings in the menu table
                            categories_deleted += 1
                            print(f"  Category '{variant}' is now empty")
        
        if duplicates_found == 0:
            print("No duplicate categories found!")
        else:
            conn.commit()
            print()
            print("=" * 60)
            print(f"Merged {duplicates_found} duplicate category groups")
            print(f"Moved {items_moved} items to canonical categories")
            print("=" * 60)
        
        conn.close()
        return duplicates_found, items_moved
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return 0, 0
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 0, 0

def cleanup_duplicates():
    """Remove duplicate menu items (case-insensitive duplicates)"""
    db_path = 'database/restaurant.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("CLEANING UP DUPLICATE ENTRIES")
        print("=" * 60)
        print()
        
        # Find duplicates (case-insensitive by name and category)
        cursor.execute('''
            SELECT 
                UPPER(name) as upper_name,
                UPPER(category) as upper_category,
                COUNT(*) as count
            FROM menu
            GROUP BY UPPER(name), UPPER(category)
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("No duplicates found!")
            conn.close()
            return 0
        
        print(f"Found {len(duplicates)} duplicate groups\n")
        
        total_deleted = 0
        
        for upper_name, upper_category, count in duplicates:
            # Get all items with this name (case-insensitive) and category
            cursor.execute('''
                SELECT id, name, category, price 
                FROM menu 
                WHERE UPPER(name) = ? AND UPPER(category) = ?
                ORDER BY id
            ''', (upper_name, upper_category))
            
            items = cursor.fetchall()
            
            if len(items) > 1:
                # Prefer uppercase names from JSON (like "BOOST/HORLICKS" over "Boost/Horlicks")
                uppercase_item = next((x for x in items if x[1].isupper()), None)
                
                if uppercase_item:
                    # Keep the uppercase version (from JSON)
                    keep_item = uppercase_item
                    delete_items = [x for x in items if x[0] != uppercase_item[0]]
                else:
                    # No uppercase version, keep the first one
                    keep_item = items[0]
                    delete_items = items[1:]
                
                print(f"Duplicate: '{upper_name}' in '{upper_category}'")
                print(f"  Keeping: {keep_item[1]} (₹{keep_item[3]}) [ID: {keep_item[0]}]")
                
                # Delete duplicates
                for item in delete_items:
                    print(f"  Deleting: {item[1]} (₹{item[3]}) [ID: {item[0]}]")
                    cursor.execute('DELETE FROM menu WHERE id = ?', (item[0],))
                    total_deleted += 1
                
                print()
        
        conn.commit()
        conn.close()
        
        print("=" * 60)
        print(f"Cleanup completed! Deleted {total_deleted} duplicate entries.")
        print("=" * 60)
        
        return total_deleted
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return 0
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 0

def update_menu_database():
    """Update menu database from JSON data"""
    db_path = 'database/restaurant.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {
            'updated': 0,
            'added': 0,
            'skipped': 0,
            'errors': 0
        }
        
        print("=" * 60)
        print("MENU DATABASE UPDATE SCRIPT")
        print("=" * 60)
        print()
        
        # Process each category
        for category_key, items in MENU_DATA.items():
            category_name = format_category_name(category_key)
            print(f"\nProcessing category: {category_name}")
            print("-" * 60)
            
            # Process each item in the category
            for item_data in items:
                item_name = item_data.get('item', '').strip()
                if not item_name:
                    stats['skipped'] += 1
                    continue
                
                # Handle items with multiple price options
                price = item_data.get('price')
                price_bone = item_data.get('price_bone')
                price_boneless = item_data.get('price_boneless')
                
                if price_bone and price_boneless:
                    # Create separate entries for bone and boneless
                    # Remove "BONE/BONELESS" from name if present, then add (BONE) and (BONELESS)
                    base_name = item_name.replace(" BONE/BONELESS", "").replace("BONE/BONELESS", "").strip()
                    items_to_process = [
                        (f"{base_name} (BONE)", price_bone),
                        (f"{base_name} (BONELESS)", price_boneless)
                    ]
                elif price:
                    items_to_process = [(item_name, price)]
                else:
                    print(f"  ⚠ Skipping '{item_name}': No price information")
                    stats['skipped'] += 1
                    continue
                
                for processed_name, processed_price in items_to_process:
                    try:
                        # Check if item exists in this category (case-insensitive comparison)
                        cursor.execute(
                            'SELECT id, name, price FROM menu WHERE UPPER(name) = UPPER(?) AND UPPER(category) = UPPER(?)',
                            (processed_name, category_name)
                        )
                        existing = cursor.fetchone()
                        
                        if existing:
                            item_id, db_name, db_price = existing
                            # Update if name (case) or price changed
                            if db_name.upper() != processed_name.upper() or db_price != processed_price:
                                cursor.execute(
                                    'UPDATE menu SET name = ?, price = ? WHERE id = ?',
                                    (processed_name, processed_price, item_id)
                                )
                                print(f"  ✓ Updated: {db_name} → {processed_name} (₹{db_price} → ₹{processed_price})")
                                stats['updated'] += 1
                            else:
                                print(f"  - No change: {processed_name} (₹{processed_price})")
                                stats['skipped'] += 1
                        else:
                            # Item doesn't exist, add it
                            cursor.execute(
                                'INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)',
                                (processed_name, category_name, processed_price, '')
                            )
                            print(f"  + Added: {processed_name} (₹{processed_price})")
                            stats['added'] += 1
                            
                    except sqlite3.Error as e:
                        print(f"  ✗ Error processing '{processed_name}': {e}")
                        stats['errors'] += 1
                        continue
        
        # Commit all changes
        conn.commit()
        
        # Print summary
        print()
        print("=" * 60)
        print("UPDATE SUMMARY")
        print("=" * 60)
        print(f"Items Updated:  {stats['updated']}")
        print(f"Items Added:    {stats['added']}")
        print(f"Items Skipped:  {stats['skipped']}")
        print(f"Errors:         {stats['errors']}")
        print("=" * 60)
        print("\nDatabase update completed successfully!")
        
        # Show category count
        cursor.execute('SELECT category, COUNT(*) FROM menu GROUP BY category ORDER BY category')
        categories = cursor.fetchall()
        print(f"\nTotal categories: {len(categories)}")
        print(f"Total items in database: {sum(count for _, count in categories)}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    import sys
    
    # Check if user wants to only cleanup duplicates
    if len(sys.argv) > 1 and sys.argv[1] == '--cleanup-only':
        deleted = cleanup_duplicates()
        print(f"\n✓ Cleanup completed! Deleted {deleted} duplicate entries.")
    elif len(sys.argv) > 1 and sys.argv[1] == '--cleanup-categories-only':
        duplicates, items_moved = cleanup_category_duplicates()
        print(f"\n✓ Category cleanup completed! Merged {duplicates} duplicate category groups.")
    else:
        # First cleanup duplicate categories
        print("Step 1: Cleaning up duplicate categories...")
        print()
        duplicates, items_moved = cleanup_category_duplicates()
        print()
        
        # Then cleanup duplicate items
        print("Step 2: Cleaning up duplicate menu items...")
        print()
        deleted = cleanup_duplicates()
        print()
        
        # Finally update the database
        print("Step 3: Updating menu database...")
        print()
        success = update_menu_database()
        
        if success:
            print("\n✓ Script completed successfully!")
        else:
            print("\n✗ Script completed with errors!")

