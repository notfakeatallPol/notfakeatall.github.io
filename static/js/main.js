// Main JavaScript for Secure Submission System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle status filter change
    const statusFilter = document.getElementById('status');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    }
    
    // Preview image before upload
    const imageInput = document.querySelector('input[type="file"]');
    const previewContainer = document.getElementById('image-preview');
    
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Only process image files
                if (!file.type.match('image.*')) {
                    return;
                }
                
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const previewWrapper = document.createElement('div');
                    previewWrapper.className = 'submission-image-container border rounded mb-2';
                    
                    const previewImg = document.createElement('img');
                    previewImg.src = e.target.result;
                    previewImg.className = 'submission-image';
                    previewImg.alt = 'Image Preview';
                    
                    previewWrapper.appendChild(previewImg);
                    previewContainer.appendChild(previewWrapper);
                    
                    const previewCaption = document.createElement('div');
                    previewCaption.className = 'form-text text-center';
                    previewCaption.textContent = 'Preview of selected image';
                    previewContainer.appendChild(previewCaption);
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-error)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});