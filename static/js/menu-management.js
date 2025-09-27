// Menu Management JavaScript

// DOM Elements
const addMenuForm = document.getElementById('add-menu-form');
const imagePreview = document.getElementById('image-preview');
const imageInput = document.getElementById('item-image');
const imageUrlInput = document.getElementById('item-image-url');
const previewImg = document.getElementById('preview-img');
const uploadPlaceholder = document.querySelector('.upload-placeholder');
const imageActions = document.getElementById('image-actions');
const removeImageBtn = document.getElementById('remove-image');
const menuItemsGrid = document.getElementById('menu-items-grid');
const filterBtns = document.querySelectorAll('.filter-btn');

// State
let currentFilter = 'all';
let currentImageFile = null;
let currentImageUrl = '';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadMenuItems();
});

function setupEventListeners() {
    // Image upload
    imagePreview.addEventListener('click', () => {
        if (!previewImg.style.display || previewImg.style.display === 'none') {
            imageInput.click();
        }
    });
    
    imageInput.addEventListener('change', handleImageUpload);
    imageUrlInput.addEventListener('input', handleImageUrlChange);
    removeImageBtn.addEventListener('click', removeImage);
    
    // Form submission
    addMenuForm.addEventListener('submit', handleFormSubmit);
    
    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => filterItems(btn.dataset.category));
    });
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            showToast('File size must be less than 5MB', 'error');
            return;
        }
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showToast('Please select a valid image file', 'error');
            return;
        }
        
        currentImageFile = file;
        currentImageUrl = '';
        imageUrlInput.value = '';
        
        const reader = new FileReader();
        reader.onload = function(e) {
            showImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
    }
}

function handleImageUrlChange(event) {
    const url = event.target.value.trim();
    if (url) {
        currentImageUrl = url;
        currentImageFile = null;
        imageInput.value = '';
        showImagePreview(url);
    } else {
        removeImage();
    }
}

function showImagePreview(src) {
    previewImg.src = src;
    previewImg.style.display = 'block';
    uploadPlaceholder.style.display = 'none';
    imageActions.style.display = 'flex';
}

function removeImage() {
    previewImg.style.display = 'none';
    uploadPlaceholder.style.display = 'flex';
    imageActions.style.display = 'none';
    currentImageFile = null;
    currentImageUrl = '';
    imageInput.value = '';
    imageUrlInput.value = '';
}

function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('item-name').value.trim(),
        category: document.getElementById('item-category').value,
        price: parseFloat(document.getElementById('item-price').value),
        prep_time: document.getElementById('item-prep-time').value || null,
        description: document.getElementById('item-description').value.trim(),
        spicy: document.getElementById('item-spicy').checked,
        vegetarian: document.getElementById('item-vegetarian').checked,
        available: document.getElementById('item-available').checked,
        image: currentImageUrl || (currentImageFile ? URL.createObjectURL(currentImageFile) : '')
    };
    
    // Validation
    if (!formData.name || !formData.category || !formData.price || isNaN(formData.price)) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    if (formData.price <= 0) {
        showToast('Price must be greater than 0', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = addMenuForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Item...';
    submitBtn.disabled = true;
    
    // Send data to server
    fetch('/api/add-menu-item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Menu item added successfully!', 'success');
            resetForm();
            loadMenuItems(); // Refresh the menu
            updateStats();
        } else {
            showToast(data.message || 'Failed to add menu item', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding menu item:', error);
        showToast('Failed to add menu item. Please try again.', 'error');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function resetForm() {
    addMenuForm.reset();
    removeImage();
    document.getElementById('item-available').checked = true;
}

function loadMenuItems() {
    fetch('/api/menu')
        .then(response => response.json())
        .then(data => {
            displayMenuItems(data);
            updateStats();
        })
        .catch(error => {
            console.error('Error loading menu items:', error);
            showToast('Failed to load menu items', 'error');
        });
}

function displayMenuItems(items) {
    const filteredItems = currentFilter === 'all' ? items : items.filter(item => item.category === currentFilter);
    
    if (filteredItems.length === 0) {
        menuItemsGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #64748b;">
                <i class="fas fa-utensils" style="font-size: 48px; margin-bottom: 16px; color: #cbd5e1;"></i>
                <h3>No menu items found</h3>
                <p>${currentFilter === 'all' ? 'Add your first menu item to get started' : `No items in ${currentFilter} category`}</p>
            </div>
        `;
        return;
    }
    
    menuItemsGrid.innerHTML = filteredItems.map(item => createMenuItemHTML(item)).join('');
}

function createMenuItemHTML(item) {
    const badges = [];
    if (item.spicy) badges.push('<span class="badge spicy"><i class="fas fa-pepper-hot"></i></span>');
    if (item.vegetarian) badges.push('<span class="badge vegetarian"><i class="fas fa-leaf"></i></span>');
    if (!item.available) badges.push('<span class="badge unavailable"><i class="fas fa-times"></i></span>');
    
    return `
        <div class="menu-item-card" data-category="${item.category}" data-item-id="${item.id}">
            <div class="menu-item-image">
                ${item.image ? 
                    `<img src="${item.image}" alt="${item.name}" loading="lazy">` :
                    `<div class="image-placeholder"><i class="fas fa-image"></i></div>`
                }
                ${badges.length > 0 ? `<div class="item-badges">${badges.join('')}</div>` : ''}
            </div>
            
            <div class="menu-item-content">
                <div class="item-header">
                    <h3>${item.name}</h3>
                    <span class="item-price">LKR ${item.price.toFixed(2)}</span>
                </div>
                <p class="item-category">${item.category}</p>
                <p class="item-description">${item.description || 'No description available'}</p>
                ${item.prep_time ? `
                    <div class="prep-time">
                        <i class="fas fa-clock"></i>
                        <span>${item.prep_time} mins</span>
                    </div>
                ` : ''}
            </div>

            <div class="item-actions">
                <button class="btn-edit" onclick="editItem('${item.id}')">
                    <i class="fas fa-edit"></i>
                    Edit
                </button>
                <button class="btn-toggle-availability" onclick="toggleAvailability('${item.id}', ${!item.available})">
                    <i class="fas fa-${item.available ? 'eye-slash' : 'eye'}"></i>
                    ${item.available ? 'Hide' : 'Show'}
                </button>
                <button class="btn-delete" onclick="deleteItem('${item.id}')">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        </div>
    `;
}

function filterItems(category) {
    currentFilter = category;
    
    // Update filter buttons
    filterBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
    
    // Reload items with filter
    loadMenuItems();
}

function editItem(itemId) {
    showToast('Edit functionality coming soon!', 'info');
    // TODO: Implement edit functionality
}

function toggleAvailability(buttonElement) {
    const itemId = buttonElement.dataset.itemId;
    const currentAvailability = buttonElement.dataset.currentAvailability === 'true';
    const newAvailability = !currentAvailability;
    
    fetch(`/api/menu-item/${itemId}/availability`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ available: newAvailability })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast(`Item ${newAvailability ? 'shown' : 'hidden'} successfully!`, 'success');
            loadMenuItems();
        } else {
            showToast(data.message || 'Failed to update item', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating availability:', error);
        showToast('Failed to update item availability', 'error');
    });
}

function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        return;
    }
    
    fetch(`/api/menu-item/${itemId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Item deleted successfully!', 'success');
            loadMenuItems();
        } else {
            showToast(data.message || 'Failed to delete item', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting item:', error);
        showToast('Failed to delete item', 'error');
    });
}

function updateStats() {
    fetch('/api/menu/stats')
        .then(response => response.json())
        .then(stats => {
            document.getElementById('total-items').textContent = stats.total || 0;
            document.getElementById('available-items').textContent = stats.available || 0;
        })
        .catch(error => console.error('Error updating stats:', error));
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle';
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}