import { escapeHtml } from '../utils/helpers.js';

// --- DOM Элементы для авторизации ---
const registerModal = document.getElementById('registerModal');
const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const modalTitle = document.getElementById('modalTitle');
const profileBtn = document.querySelector('.profile-btn');
const greetingSpan = document.getElementById('userGreeting');

// Состояние
let isRegistered = false;

// --- Вспомогательные функции ---

function clearErrors() {
    document.getElementById('registerError').textContent = '';
    document.getElementById('loginError').textContent = '';
    document.getElementById('regUsername').value = '';
    document.getElementById('regEmail').value = '';
    document.getElementById('regPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    document.getElementById('loginEmail').value = '';
    document.getElementById('loginPassword').value = '';
}

function validatePassword(password, confirmPassword) {
    if (password !== confirmPassword) return 'Пароли не совпадают';
    if (password.length < 6) return 'Пароль должен содержать минимум 6 символов';
    return null;
}

// --- Публичные функции ---

export function openRegisterModal() {
    registerModal.style.display = 'block';
    showRegisterForm();
}

export function closeRegisterModal() {
    registerModal.style.display = 'none';
    clearErrors();
}

export function showRegisterForm() {
    registerForm.classList.add('active');
    loginForm.classList.remove('active');
    modalTitle.textContent = 'Регистрация';
    clearErrors();
}

export function showLoginForm() {
    loginForm.classList.add('active');
    registerForm.classList.remove('active');
    modalTitle.textContent = 'Авторизация';
    clearErrors();
}

export function updateProfileButton(username) {
    if (profileBtn) {
        profileBtn.innerHTML = `<img src="../../images/user.svg" alt="user" width="16" height="16" style="opacity:0.6; margin-right: 6px;"> ${escapeHtml(username)}`;
    }
}

export function updateGreeting() {
    if (greetingSpan) {
        const userData = localStorage.getItem('currentUser');
        if (userData) {
            try {
                const user = JSON.parse(userData);
                greetingSpan.textContent = user.username || 'Гость';
            } catch (e) {
                greetingSpan.textContent = 'Гость';
            }
        } else {
            greetingSpan.textContent = 'Гость';
        }
    }
}

// --- Обработчики событий (будут вызваны из app.js) ---
export function initAuth() {
    // Обработка регистрации
    registerForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('regUsername').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const errorElement = document.getElementById('registerError');
        
        if (!username) { errorElement.textContent = 'Введите имя пользователя'; return; }
        if (!email || !email.includes('@')) { errorElement.textContent = 'Введите корректный email'; return; }
        
        const passwordError = validatePassword(password, confirmPassword);
        if (passwordError) { errorElement.textContent = passwordError; return; }
        
        if (localStorage.getItem(`user_${email}`)) {
            errorElement.textContent = 'Пользователь с таким email уже существует';
            return;
        }
        
        const userData = { username, email, password: btoa(password), registeredAt: new Date().toISOString() };
        localStorage.setItem(`user_${email}`, JSON.stringify(userData));
        localStorage.setItem('currentUser', JSON.stringify({ username, email }));
        
        alert(`Добро пожаловать, ${username}!`);
        closeRegisterModal();
        updateProfileButton(username);
        updateGreeting();
    });

    // Обработка авторизации
    loginForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const errorElement = document.getElementById('loginError');
        
        if (!email || !email.includes('@')) { errorElement.textContent = 'Введите корректный email'; return; }
        if (!password) { errorElement.textContent = 'Введите пароль'; return; }
        
        const userDataStr = localStorage.getItem(`user_${email}`);
        if (!userDataStr) { errorElement.textContent = 'Пользователь с таким email не найден'; return; }
        
        try {
            const userData = JSON.parse(userDataStr);
            if (btoa(password) !== userData.password) { errorElement.textContent = 'Неверный пароль'; return; }
            
            localStorage.setItem('currentUser', JSON.stringify({ username: userData.username, email: userData.email }));
            alert(`С возвращением, ${userData.username}!`);
            closeRegisterModal();
            updateProfileButton(userData.username);
            updateGreeting();
        } catch (e) {
            errorElement.textContent = 'Ошибка при входе. Попробуйте снова.';
        }
    });

    // Переключение форм
    document.getElementById('switchToLogin')?.addEventListener('click', showLoginForm);
    document.getElementById('switchToRegister')?.addEventListener('click', showRegisterForm);

    // Закрытие модалки
    document.querySelector('.modal-close')?.addEventListener('click', closeRegisterModal);
    window.addEventListener('click', (e) => { if (e.target === registerModal) closeRegisterModal(); });

    // Инициализация кнопки профиля
    if (profileBtn) {
        profileBtn.addEventListener('click', openRegisterModal);
        const currentUser = localStorage.getItem('currentUser');
        if (currentUser) {
            try {
                updateProfileButton(JSON.parse(currentUser).username);
            } catch(e) {}
        }
    }
    
    // Проверка сессии при загрузке
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser) {
        try {
            updateProfileButton(JSON.parse(currentUser).username);
        } catch(e) {}
    }
    updateGreeting();
}