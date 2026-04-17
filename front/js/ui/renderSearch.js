import { tracks } from '../data/data.js';
import { switchToPage } from './ui.js';
import { escapeHtml, getDeclension } from '../utils/helpers.js';

const searchInput = document.getElementById('searchInput');
const searchResultsContainer = document.getElementById('searchResultsList');
const searchStats = document.getElementById('searchStats');
const clearSearchBtn = document.getElementById('clearSearchBtn');

let currentSearchQuery = '';

export function performSearch() {
    const query = searchInput.value.trim().toLowerCase();
    currentSearchQuery = query;
    
    if (!query) {
        searchStats.textContent = '🔍 Введите название трека, альбома или исполнителя';
        searchResultsContainer.innerHTML = '';
        return;
    }
    
    const filtered = tracks.filter(track => 
        track.name.toLowerCase().includes(query) || 
        track.album.toLowerCase().includes(query) || 
        track.artist.toLowerCase().includes(query)
    );
    
    if (filtered.length === 0) {
        searchStats.textContent = `😔 Ничего не найдено по запросу "${escapeHtml(query)}"`;
        searchResultsContainer.innerHTML = `<div class="no-results">🎵 Ничего не найдено<br>Попробуйте другой запрос</div>`;
        return;
    }
    
    searchStats.textContent = `🎵 Найдено ${filtered.length} трек${getDeclension(filtered.length)} по запросу "${escapeHtml(query)}"`;
    
    let resultsHtml = '';
    filtered.forEach(track => {
        resultsHtml += `
            <div class="track-item" data-track-id="${track.id}" data-source="favorites">
                <div class="track-container">
                    <div class="track-image">
                        <div class="track-artwork">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M9 18V5l12-2v13" />
                                <circle cx="6" cy="18" r="3" />
                                <circle cx="18" cy="16" r="3" />
                            </svg>
                        </div>
                    </div>
                    <div class="track-info">
                        <div class="track-name">${escapeHtml(track.name)}</div>
                        <div class="track-artist">${escapeHtml(track.artist)}</div>
                    </div>
                </div>
                <div class="track-time">${track.duration}</div>
            </div>
        `;
    });
    searchResultsContainer.innerHTML = resultsHtml;
}

export function clearSearch() {
    searchInput.value = '';
    performSearch();
    searchInput.focus();
}

export function initSearch() {
    searchInput.addEventListener('input', performSearch);
    clearSearchBtn.addEventListener('click', clearSearch);
    
    // Обработчики для быстрых карточек
    document.addEventListener('click', (e) => {
        const quickCard = e.target.closest('.quick-card');
        if (quickCard) {
            const text = quickCard.querySelector('span')?.textContent;
            if (text === 'Любимые треки') {
                switchToPage('favorites');
            } else if (text === 'Популярное') {
                switchToPage('search');
                setTimeout(() => { searchInput.value = 'New track'; performSearch(); }, 100);
            }
        }
        
        const seeAllBtn = e.target.closest('.see-all-btn');
        if (seeAllBtn && seeAllBtn.dataset.section === 'popular') {
            switchToPage('search');
            setTimeout(() => { searchInput.value = 'New track'; performSearch(); }, 100);
        }
    });
}