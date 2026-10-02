document.addEventListener('DOMContentLoaded', function () {
    const root = document.body;
    const toggle = document.getElementById('theme-toggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem('pocketsmart-theme');
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        root.classList.add('dark-mode');
        if (toggle) toggle.textContent = '☀️';
    }

    if (toggle) {
        toggle.addEventListener('click', function () {
            root.classList.toggle('dark-mode');
            const dark = root.classList.contains('dark-mode');
            localStorage.setItem('pocketsmart-theme', dark ? 'dark' : 'light');
            toggle.textContent = dark ? '☀️' : '🌙';
        });
    }

    document.querySelectorAll('form[data-validate="true"]').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const budgetInput = form.querySelector('input[name="total_budget"], input[name="budget"]');
            if (budgetInput && Number(budgetInput.value) <= 0) {
                event.preventDefault();
                showToast('Budget must be greater than zero.', 'error');
            }
        });
    });

    const fileInput = document.querySelector('input[type="file"][name="image"]');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const file = this.files && this.files[0];
            if (!file) return;
            const allowed = ['image/jpeg', 'image/png', 'image/webp'];
            if (!allowed.includes(file.type)) {
                showToast('Invalid image type. Use PNG, JPG, or WEBP.', 'error');
                this.value = '';
                return;
            }
            if (file.size > 2 * 1024 * 1024) {
                showToast('Image is too large. Maximum 2MB.', 'error');
                this.value = '';
                return;
            }
            const preview = document.createElement('img');
            preview.className = 'uploaded-image';
            preview.src = URL.createObjectURL(file);
            const existing = document.querySelector('.uploaded-image');
            if (existing) existing.remove();
            fileInput.parentElement.insertAdjacentElement('afterend', preview);
        });
    }

    document.querySelectorAll('[data-confirm]').forEach(function (button) {
        button.addEventListener('click', function (event) {
            const confirmed = confirm('Are you sure you want to continue?');
            if (!confirmed) event.preventDefault();
        });
    });
});

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.textContent = message;
    document.getElementById('toast-container').appendChild(toast);
    setTimeout(function () {
        toast.remove();
    }, 3000);
}
