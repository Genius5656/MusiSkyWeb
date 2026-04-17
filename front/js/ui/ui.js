// Этот модуль управляет состоянием UI: активная страница, контейнеры и переключение.
import { renderHomeContent } from './renderHome.js';
import { renderPlaylistPage } from './renderPlaylist.js';
import { closePlayerIfNeeded } from '../player/player.js';

// --- DOM Элементы ---
export const mainContent = document.getElementById('mainContent');
export const homePage = document.getElementById('homePage');
export const favoritesPage = document.getElementById('favoritesPage');
export const searchPage = document.getElementById('searchPage');
export const homeNavBtn = document.querySelector('.nav-item:first-child');
export const searchNavBtn = document.getElementById('searchNavBtn');
export const favoritesBtn = document.getElementById('favoritesBtn');
export const playlistsContainer = document.getElementById('playlistsContainer');

// Контейнер для динамических страниц плейлистов
export let playlistPagesContainer = null;

export function initPlaylistPagesContainer() {
    if (!playlistPagesContainer) {
        playlistPagesContainer = document.createElement('div');
        playlistPagesContainer.id = 'playlistPagesContainer';
        mainContent.appendChild(playlistPagesContainer);
    }
}

// --- Навигация ---

/**
 * Скрывает все страницы контента (главная, избранное, поиск, все плейлисты).
 */
function hideAllPages() {
    homePage.classList.remove('active-page');
    favoritesPage.classList.remove('active-page');
    searchPage.classList.remove('active-page');
    document.querySelectorAll('.playlist-page').forEach(page => {
        page.classList.remove('active-page');
    });
}

/**
 * Сбрасывает активный класс со всех кнопок навигации.
 */
function deactivateAllNavButtons() {
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
}

/**
 * Переключает отображение на указанный плейлист.
 * @param {object} playlist - Объект плейлиста.
 */
export function switchToPlaylist(playlist) {
    hideAllPages();
    const page = renderPlaylistPage(playlist);
    page.classList.add('active-page');
    
    deactivateAllNavButtons();
    const playlistBtn = document.querySelector(`.nav-item[data-playlist-id="${playlist.id}"]`);
    if (playlistBtn) playlistBtn.classList.add('active');
    
    closePlayerIfNeeded();
}

/**
 * Переключает отображение на одну из главных страниц (home, favorites, search).
 * @param {string} pageName - Имя страницы ('home', 'favorites', 'search').
 */
export function switchToPage(pageName) {
    hideAllPages();
    deactivateAllNavButtons();
    
    if (pageName === 'home') {
        homePage.classList.add('active-page');
        if (homeNavBtn) homeNavBtn.classList.add('active');
        renderHomeContent();
    } else if (pageName === 'favorites') {
        favoritesPage.classList.add('active-page');
        favoritesBtn.classList.add('active');
    } else if (pageName === 'search') {
        searchPage.classList.add('active-page');
        searchNavBtn.classList.add('active');
        // Фокус на поиск и выполнение поиска будет в renderSearch модуле
    }
    closePlayerIfNeeded();
}