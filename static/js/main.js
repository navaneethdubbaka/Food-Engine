// Main JavaScript for Restaurant Billing System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Global variables
let currentBill = [];
let currentCategory = '';

// Category selection
function selectCategory(category) {
    currentCategory = category;
    
    // Update active category items (both old and new layouts)
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.classList.remove('active');
    });
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to clicked element
    if (event.target.classList.contains('category-item')) {
        event.target.classList.add('active');
    } else if (event.target.closest('.category-item')) {
        event.target.closest('.category-item').classList.add('active');
    }
    
    // Update category title in middle section
    const categoryTitle = document.getElementById('current-category-title');
    if (categoryTitle) {
        categoryTitle.textContent = category;
    }
    
    // Load menu items for this category
    loadMenuItems(category);
}

// Load menu items by category
async function loadMenuItems(category) {
    try {
        const response = await fetch(`/api/menu_items/${category}`);
        const items = await response.json();
        
        const menuContainer = document.getElementById('menu-items-container');
        menuContainer.innerHTML = '';
        
        if (items.length === 0) {
            menuContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-exclamation-circle text-muted" style="font-size: 3rem;"></i>
                    <h5 class="text-muted mt-3">No items in this category</h5>
                    <p class="text-muted">Add some menu items to get started.</p>
                </div>
            `;
            return;
        }
        
        items.forEach(item => {
            const itemCard = createMenuItemCard(item);
            menuContainer.appendChild(itemCard);
        });
        
        // Update language for newly loaded items
        if (typeof refreshLanguage === 'function') {
            refreshLanguage();
        }
    } catch (error) {
        console.error('Error loading menu items:', error);
        showAlert('Error loading menu items', 'danger');
    }
}

// Create menu item card
function createMenuItemCard(item) {
    const card = document.createElement('div');
    card.className = 'menu-item-card';
    
    const imageSrc = item.image ? `/static/images/${item.image}` : '/static/images/placeholder.svg';
    
    card.innerHTML = `
        <img src="${imageSrc}" 
             alt="${item.name}" class="menu-item-image" 
             onerror="this.src='/static/images/placeholder.svg'">
        <div class="menu-item-info">
            <div class="menu-item-name">${item.name}</div>
            <div class="menu-item-price">₹${item.price.toFixed(2)}</div>
            ${item.description ? `<div class="menu-item-description">${item.description}</div>` : ''}
        </div>
    `;
    
    // Add click event
    card.onclick = () => addToBill(item.id, item.name, item.price, item.image || '');
    
    return card;
}

// Add item to bill
function addToBill(itemId, name, price, image) {
    const existingItem = currentBill.find(item => item.id === itemId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        currentBill.push({
            id: itemId,
            name: name,
            price: price,
            quantity: 1,
            image: image
        });
    }
    
    updateBillDisplay();
    showAlert(`${name} added to bill`, 'success');
}

// Update bill display
function updateBillDisplay() {
    const billContainer = document.getElementById('bill-items');
    const subtotalElement = document.getElementById('bill-subtotal');
    const taxElement = document.getElementById('bill-tax');
    const serviceChargeElement = document.getElementById('bill-service-charge');
    const totalElement = document.getElementById('bill-total');
    
    if (currentBill.length === 0) {
        billContainer.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-cart-x" style="font-size: 2rem;"></i>
                <p class="mt-2" data-lang="billing.no_items">No items in bill</p>
            </div>
        `;
        if (subtotalElement) subtotalElement.textContent = '₹0.00';
        if (taxElement) taxElement.textContent = '₹0.00';
        if (serviceChargeElement) serviceChargeElement.textContent = '₹0.00';
        if (totalElement) totalElement.textContent = '₹0.00';
        return;
    }
    
    // Calculate totals
    const subtotal = currentBill.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const taxRateElement = document.getElementById('tax-rate');
    const serviceChargeRateElement = document.getElementById('service-charge-rate');
    const taxRate = taxRateElement ? parseFloat(taxRateElement.textContent) || 10 : 10;
    const serviceChargeRate = serviceChargeRateElement ? parseFloat(serviceChargeRateElement.textContent) || 5 : 5;
    
    const taxAmount = (subtotal * taxRate) / 100;
    const serviceCharge = (subtotal * serviceChargeRate) / 100;
    const total = subtotal + taxAmount + serviceCharge;
    
    // Update bill items
    billContainer.innerHTML = '';
    currentBill.forEach(item => {
        const billItem = createBillItem(item);
        billContainer.appendChild(billItem);
    });
    
    // Update totals
    if (subtotalElement) subtotalElement.textContent = `₹${subtotal.toFixed(2)}`;
    if (taxElement) taxElement.textContent = `₹${taxAmount.toFixed(2)}`;
    if (serviceChargeElement) serviceChargeElement.textContent = `₹${serviceCharge.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `₹${total.toFixed(2)}`;
}

// Create bill item element
function createBillItem(item) {
    const div = document.createElement('div');
    div.className = 'bill-item';
    div.innerHTML = `
        <div class="bill-item-info">
            <div class="bill-item-name">${item.name}</div>
            <div class="bill-item-quantity">₹${item.price.toFixed(2)} × ${item.quantity}</div>
        </div>
        <div class="d-flex align-items-center">
            <div class="quantity-controls me-3">
                <button class="quantity-btn" onclick="updateQuantity(${item.id}, -1)">
                    <i class="bi bi-dash"></i>
                </button>
                <input type="number" class="quantity-input" value="${item.quantity}" 
                       min="1" onchange="setQuantity(${item.id}, this.value)">
                <button class="quantity-btn" onclick="updateQuantity(${item.id}, 1)">
                    <i class="bi bi-plus"></i>
                </button>
            </div>
            <div class="bill-item-price me-3">₹${(item.price * item.quantity).toFixed(2)}</div>
            <button class="btn btn-outline-danger btn-sm" onclick="removeFromBill(${item.id})">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    return div;
}

// Update item quantity
function updateQuantity(itemId, change) {
    const item = currentBill.find(item => item.id === itemId);
    if (item) {
        item.quantity = Math.max(1, item.quantity + change);
        updateBillDisplay();
    }
}

// Set item quantity
function setQuantity(itemId, quantity) {
    const item = currentBill.find(item => item.id === itemId);
    if (item) {
        item.quantity = Math.max(1, parseInt(quantity));
        updateBillDisplay();
    }
}

// Remove item from bill
function removeFromBill(itemId) {
    currentBill = currentBill.filter(item => item.id !== itemId);
    updateBillDisplay();
    showAlert('Item removed from bill', 'info');
}

// Generate bill
async function generateBill() {
    if (currentBill.length === 0) {
        showAlert('Please add items to the bill first', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/generate_bill', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                items: currentBill
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Clear current bill
            currentBill = [];
            updateBillDisplay();
            
            // Show success message
            showAlert('Bill generated successfully!', 'success');
            
            // Open bill in same tab
            window.location.href = `/bill/${result.bill_number}`;
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error generating bill:', error);
        showAlert('Error generating bill', 'danger');
    }
}

// Clear bill
function clearBill() {
    if (currentBill.length === 0) {
        showAlert('Bill is already empty', 'info');
        return;
    }
    
    if (confirm('Are you sure you want to clear the bill?')) {
        currentBill = [];
        updateBillDisplay();
        showAlert('Bill cleared', 'info');
    }
}

// Show alert message
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Create alert container if it doesn't exist
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Menu Management Functions
function openAddItemModal() {
    const modal = new bootstrap.Modal(document.getElementById('addItemModal'));
    modal.show();
}

function openEditItemModal(itemId, name, category, price, description) {
    document.getElementById('edit-item-id').value = itemId;
    document.getElementById('edit-item-name').value = name;
    document.getElementById('edit-item-category').value = category;
    document.getElementById('edit-item-price').value = price;
    document.getElementById('edit-item-description').value = description;
    
    const modal = new bootstrap.Modal(document.getElementById('editItemModal'));
    modal.show();
}

function openDeleteItemModal(itemId, itemName) {
    document.getElementById('delete-item-id').value = itemId;
    document.getElementById('delete-item-name').textContent = itemName;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteItemModal'));
    modal.show();
}

// Add menu item
async function addMenuItem() {
    const form = document.getElementById('addItemForm');
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/add_menu_item', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Menu item added successfully', 'success');
            form.reset();
            bootstrap.Modal.getInstance(document.getElementById('addItemModal')).hide();
            location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error adding menu item:', error);
        showAlert('Error adding menu item', 'danger');
    }
}

// Update menu item
async function updateMenuItem() {
    const form = document.getElementById('editItemForm');
    const formData = new FormData(form);
    const itemId = document.getElementById('edit-item-id').value;
    
    try {
        const response = await fetch(`/api/update_menu_item/${itemId}`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Menu item updated successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editItemModal')).hide();
            location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error updating menu item:', error);
        showAlert('Error updating menu item', 'danger');
    }
}

// Delete menu item
async function deleteMenuItem() {
    const itemId = document.getElementById('delete-item-id').value;
    
    try {
        const response = await fetch(`/api/delete_menu_item/${itemId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Menu item deleted successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('deleteItemModal')).hide();
            location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error deleting menu item:', error);
        showAlert('Error deleting menu item', 'danger');
    }
}

// Settings functions
async function updateSettings() {
    const form = document.getElementById('settingsForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/update_settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Settings updated successfully', 'success');
            location.reload();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        console.error('Error updating settings:', error);
        showAlert('Error updating settings', 'danger');
    }
}

// Image upload handling
function handleImageUpload(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = input.parentNode.querySelector('.image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }
}

// Initialize page
function initializePage() {
    // Load settings for bill calculation
    loadSettings();
    
    // Set up image upload areas
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            handleImageUpload(this);
        });
    });
}

// Load settings
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        // Update bill calculation elements
        const taxRateElement = document.getElementById('tax-rate');
        const serviceChargeRateElement = document.getElementById('service-charge-rate');
        
        if (taxRateElement) {
            taxRateElement.textContent = settings.tax_rate || '10';
        }
        if (serviceChargeRateElement) {
            serviceChargeRateElement.textContent = settings.service_charge_rate || '5';
        }
        
        // Update restaurant name in navbar
        const restaurantNameElement = document.getElementById('restaurant-name');
        if (restaurantNameElement) {
            restaurantNameElement.textContent = settings.restaurant_name || 'Restaurant Billing';
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePage);
