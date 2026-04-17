/**
 * Главный модуль приложения. Импортирует и инициализирует все остальные модули.
 */

import { initAuth, updateGreeting } from './auth/auth.js';
import { initPlayer } from './player/player.js';
import { 
    initPlaylistPagesContainer, 
    switchToPage, 
    homeNavBtn, 
    searchNavBtn, 
    favoritesBtn, 
    playlistsContainer 
} from './ui/ui.js';
import { 
    renderFavorites 
} from './ui/renderFavorites.js';
import { 
    initSearch, 
    performSearch 
} from './ui/renderSearch.js';
import { 
    renderExistingPlaylists, 
    addNewPlaylist 
} from './ui/renderPlaylist.js';
import { closePlayerIfNeeded } from './player/player.js';

// --- Инициализация приложения ---
function initApp() {
    // 1. Инициализация контейнера для страниц плейлистов
    initPlaylistPagesContainer();
    
    // 2. Инициализация модулей с их DOM-элементами и слушателями
    initAuth();
    initPlayer();
    initSearch();
    
    // 3. Рендеринг начального состояния
    renderFavorites();
    performSearch();
    renderExistingPlaylists();
    
    // 4. Установка обработчиков навигации
    if (homeNavBtn) {
        homeNavBtn.addEventListener('click', () => {
            switchToPage('home');
            closePlayerIfNeeded();
        });
    }
    
    favoritesBtn.addEventListener('click', () => {
        switchToPage('favorites');
        closePlayerIfNeeded();
    });
    
    searchNavBtn.addEventListener('click', () => {
        switchToPage('search');
        closePlayerIfNeeded();
        performSearch(); // Обновляем результаты при переходе
    });
    
    const createPlaylistBtn = document.getElementById('createPlaylistBtn');
    createPlaylistBtn.addEventListener('click', addNewPlaylist);
    
    // 5. Загружаем домашнюю страницу по умолчанию
    switchToPage('home');
    updateGreeting();
    
    console.log('Приложение инициализировано. Добро пожаловать!');
}

// Запускаем приложение после полной загрузки DOM
document.addEventListener('DOMContentLoaded', initApp);