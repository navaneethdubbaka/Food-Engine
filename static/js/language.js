// Language support for Restaurant Billing System
const languages = {
    en: {
        // Navigation
        'nav.restaurant_name': 'Restaurant Billing',
        'nav.billing': 'Billing',
        'nav.menu': 'Menu',
        'nav.reports': 'Reports',
        'nav.settings': 'Settings',
        
        // Billing Page
        'billing.title': 'Menu Items',
        'billing.select_category': 'Select Category:',
        'billing.current_bill': 'Current Bill',
        'billing.no_items': 'No items in bill',
        'billing.subtotal': 'Subtotal:',
        'billing.tax': 'Tax',
        'billing.service_charge': 'Service Charge',
        'billing.total': 'Total:',
        'billing.generate_bill': 'Generate Bill',
        'billing.clear_bill': 'Clear Bill',
        
        // Menu Page
        'menu.title': 'Menu Management',
        'menu.add_item': 'Add Menu Item',
        'menu.name': 'Item Name',
        'menu.category': 'Category',
        'menu.price': 'Price',
        'menu.description': 'Description',
        'menu.image': 'Image',
        'menu.actions': 'Actions',
        'menu.edit': 'Edit',
        'menu.delete': 'Delete',
        
        // Reports Page
        'reports.title': 'Sales Reports & Bills History',
        'reports.export_csv': 'Export CSV',
        'reports.refresh': 'Refresh',
        'reports.filter_month': 'Filter by Month',
        'reports.all_months': 'All Months',
        'reports.filter': 'Filter',
        'reports.filter_status': 'Filter Status',
        'reports.showing_all': 'Showing all bills',
        'reports.showing_month': 'Showing bills for',
        'reports.from_date': 'From Date',
        'reports.to_date': 'To Date',
        'reports.search_bill': 'Search Bill',
        'reports.bill_placeholder': 'Bill number...',
        'reports.clear_filters': 'Clear Filters',
        'reports.total_bills': 'Total Bills',
        'reports.total_sales': 'Total Sales',
        'reports.today_sales': 'Today\'s Sales',
        'reports.monthly_sales': 'Monthly Sales',
        'reports.avg_bill': 'Average Bill',
        'reports.bills_history': 'Bills History',
        'reports.bill_number': 'Bill Number',
        'reports.date_time': 'Date & Time',
        'reports.items': 'Items',
        'reports.subtotal': 'Subtotal',
        'reports.tax': 'Tax',
        'reports.service': 'Service',
        'reports.total': 'Total',
        'reports.actions': 'Actions',
        'reports.view': 'View',
        'reports.print': 'Print',
        'reports.no_bills': 'No bills found',
        'reports.start_generating': 'Start generating bills to see them here.',
        'reports.create_first_bill': 'Create First Bill',
        
        // Settings Page
        'settings.title': 'Settings',
        'settings.restaurant_info': 'Restaurant Information',
        'settings.billing_settings': 'Billing Settings',
        'settings.restaurant_name': 'Restaurant Name',
        'settings.restaurant_address': 'Restaurant Address',
        'settings.restaurant_phone': 'Restaurant Phone',
        'settings.tax_rate': 'Tax Rate (%)',
        'settings.service_charge_rate': 'Service Charge Rate (%)',
        'settings.save': 'Save Settings',
        
        // Categories
        'category.beverage': 'Beverage',
        'category.dessert': 'Dessert',
        'category.main_course': 'Main Course',
        'category.salad': 'Salad',
        'category.side_dish': 'Side Dish',
        'category.appetizer': 'Appetizer',
        
        // Menu Items
        'menu.no_image': 'No Image',
        'menu.french_fries': 'French Fries',
        'menu.french_fries_desc': 'Crispy golden french fries',
        
        // Footer
        'footer.copyright': '© 2024 Restaurant Billing System. All rights reserved.',
        
        // Common
        'common.save': 'Save',
        'common.cancel': 'Cancel',
        'common.delete': 'Delete',
        'common.edit': 'Edit',
        'common.add': 'Add',
        'common.close': 'Close',
        'common.confirm': 'Confirm',
        'common.yes': 'Yes',
        'common.no': 'No',
        'common.back': 'Back'
    },
    
    te: {
        // Navigation
        'nav.restaurant_name': 'రెస్టారెంట్ బిల్లింగ్',
        'nav.billing': 'బిల్లింగ్',
        'nav.menu': 'మెనూ',
        'nav.reports': 'రిపోర్ట్లు',
        'nav.settings': 'సెట్టింగ్లు',
        
        // Billing Page
        'billing.title': 'మెనూ అంశాలు',
        'billing.select_category': 'వర్గాన్ని ఎంచుకోండి:',
        'billing.current_bill': 'ప్రస్తుత బిల్లు',
        'billing.no_items': 'బిల్లులో అంశాలు లేవు',
        'billing.subtotal': 'ఉప-మొత్తం:',
        'billing.tax': 'పన్ను',
        'billing.service_charge': 'సేవా ఛార్జ్',
        'billing.total': 'మొత్తం:',
        'billing.generate_bill': 'బిల్లు తయారు చేయండి',
        'billing.clear_bill': 'బిల్లు క్లియర్ చేయండి',
        
        // Menu Page
        'menu.title': 'మెనూ నిర్వహణ',
        'menu.add_item': 'మెనూ అంశం జోడించండి',
        'menu.name': 'అంశం పేరు',
        'menu.category': 'వర్గం',
        'menu.price': 'ధర',
        'menu.description': 'వివరణ',
        'menu.image': 'చిత్రం',
        'menu.actions': 'చర్యలు',
        'menu.edit': 'సవరించండి',
        'menu.delete': 'తొలగించండి',
        
        // Reports Page
        'reports.title': 'విక్రయ రిపోర్ట్లు & బిల్లు చరిత్ర',
        'reports.export_csv': 'CSV ఎగుమతి',
        'reports.refresh': 'రిఫ్రెష్',
        'reports.filter_month': 'నెల ద్వారా ఫిల్టర్ చేయండి',
        'reports.all_months': 'అన్ని నెలలు',
        'reports.filter': 'ఫిల్టర్',
        'reports.filter_status': 'ఫిల్టర్ స్థితి',
        'reports.showing_all': 'అన్ని బిల్లులు చూపిస్తున్నది',
        'reports.showing_month': 'బిల్లులు చూపిస్తున్నది',
        'reports.from_date': 'నుండి తేదీ',
        'reports.to_date': 'వరకు తేదీ',
        'reports.search_bill': 'బిల్లు వెతకండి',
        'reports.bill_placeholder': 'బిల్లు నంబర్...',
        'reports.clear_filters': 'ఫిల్టర్లు క్లియర్ చేయండి',
        'reports.total_bills': 'మొత్తం బిల్లులు',
        'reports.total_sales': 'మొత్తం విక్రయాలు',
        'reports.today_sales': 'ఈరోజు విక్రయాలు',
        'reports.monthly_sales': 'నెలవారీ విక్రయాలు',
        'reports.avg_bill': 'సగటు బిల్లు',
        'reports.bills_history': 'బిల్లులు చరిత్ర',
        'reports.bill_number': 'బిల్లు నంబర్',
        'reports.date_time': 'తేదీ & సమయం',
        'reports.items': 'అంశాలు',
        'reports.subtotal': 'ఉప-మొత్తం',
        'reports.tax': 'పన్ను',
        'reports.service': 'సేవ',
        'reports.total': 'మొత్తం',
        'reports.actions': 'చర్యలు',
        'reports.view': 'చూడండి',
        'reports.print': 'ప్రింట్',
        'reports.no_bills': 'బిల్లులు కనుగొనబడలేదు',
        'reports.start_generating': 'వాటిని ఇక్కడ చూడటానికి బిల్లులు తయారు చేయడం ప్రారంభించండి.',
        'reports.create_first_bill': 'మొదటి బిల్లు సృష్టించండి',
        
        // Settings Page
        'settings.title': 'సెట్టింగ్లు',
        'settings.restaurant_info': 'రెస్టారెంట్ సమాచారం',
        'settings.billing_settings': 'బిల్లింగ్ సెట్టింగ్లు',
        'settings.restaurant_name': 'రెస్టారెంట్ పేరు',
        'settings.restaurant_address': 'రెస్టారెంట్ చిరునామా',
        'settings.restaurant_phone': 'రెస్టారెంట్ ఫోన్',
        'settings.tax_rate': 'పన్ను రేటు (%)',
        'settings.service_charge_rate': 'సేవా ఛార్జ్ రేటు (%)',
        'settings.save': 'సెట్టింగ్లు సేవ్ చేయండి',
        
        // Categories
        'category.beverage': 'పానీయాలు',
        'category.dessert': 'మిఠాయి',
        'category.main_course': 'ప్రధాన వంటకం',
        'category.salad': 'సలాడ్',
        'category.side_dish': 'సైడ్ డిష్',
        'category.appetizer': 'ఆపెటైజర్',
        
        // Menu Items
        'menu.no_image': 'చిత్రం లేదు',
        'menu.french_fries': 'ఫ్రెంచ్ ఫ్రైస్',
        'menu.french_fries_desc': 'క్రిస్పీ గోల్డెన్ ఫ్రెంచ్ ఫ్రైస్',
        
        // Footer
        'footer.copyright': '© 2024 రెస్టారెంట్ బిల్లింగ్ సిస్టమ్. అన్ని హక్కులు ప్రత్యేకించబడ్డాయి.',
        
        // Common
        'common.save': 'సేవ్',
        'common.cancel': 'రద్దు',
        'common.delete': 'తొలగించండి',
        'common.edit': 'సవరించండి',
        'common.add': 'జోడించండి',
        'common.close': 'మూసివేయండి',
        'common.confirm': 'నిర్ధారించండి',
        'common.yes': 'అవును',
        'common.no': 'కాదు',
        'common.back': 'వెనక్కి'
    }
};

// Current language
let currentLanguage = 'en';

// Language switching functions
function switchLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    updateLanguage();
    
    // Dispatch a custom event for language change
    const event = new CustomEvent('languageChanged', { 
        detail: { language: lang } 
    });
    document.dispatchEvent(event);
}

function updateLanguage() {
    const elements = document.querySelectorAll('[data-lang]');
    elements.forEach(element => {
        const key = element.getAttribute('data-lang');
        if (languages[currentLanguage] && languages[currentLanguage][key]) {
            element.textContent = languages[currentLanguage][key];
        }
    });
    
    // Update page title if it has language support
    const titleElement = document.querySelector('title');
    if (titleElement && titleElement.getAttribute('data-lang')) {
        const titleKey = titleElement.getAttribute('data-lang');
        if (languages[currentLanguage] && languages[currentLanguage][titleKey]) {
            titleElement.textContent = languages[currentLanguage][titleKey];
        }
    }
}

// Force refresh language across all elements
function refreshLanguage() {
    updateLanguage();
    // Also update dynamic content like menu items
    updateDynamicContent();
}

// Update dynamic content that's not in the DOM initially
function updateDynamicContent() {
    // Food items remain in English - no translation needed
    // Only update interface elements like "No Image" text
    const imageElements = document.querySelectorAll('img[alt*="No Image"], img[alt*="No image"]');
    imageElements.forEach(element => {
        if (currentLanguage === 'te') {
            element.alt = 'చిత్రం లేదు';
        }
    });
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedLanguage = localStorage.getItem('language') || 'en';
    currentLanguage = savedLanguage;
    updateLanguage();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded, initialize immediately
    const savedLanguage = localStorage.getItem('language') || 'en';
    currentLanguage = savedLanguage;
    updateLanguage();
}

// Make functions globally available
window.switchLanguage = switchLanguage;
window.refreshLanguage = refreshLanguage;
