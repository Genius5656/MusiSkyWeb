import { popularTracks, newReleases, recommendedTracks, recommendedPlaylists, tracks } from '../data/data.js';
import { switchToPlaylist } from './ui.js';
import { openPlayer } from '../player/player.js';
import { escapeHtml } from '../utils/helpers.js';
import { updateGreeting } from '../auth/auth.js';

export function renderHomeContent() {
    renderPopularTracks();
    renderRecommendedPlaylists();
    renderNewReleases();
    renderRecommendedTracks();
    updateGreeting();
}

function renderPopularTracks() {
    const container = document.getElementById('popularTracksGrid');
    if (!container) return;
    
    const topTracks = popularTracks.slice(0, 8);
    container.innerHTML = topTracks.map(track => createTrackCard(track)).join('');
    attachTrackCardListeners(container);
}

function renderNewReleases() {
    const container = document.getElementById('newReleasesGrid');
    if (!container) return;
    
    const newTracks = newReleases.slice(0, 8);
    container.innerHTML = newTracks.map(track => createTrackCard(track)).join('');
    attachTrackCardListeners(container);
}

function renderRecommendedTracks() {
    const container = document.getElementById('recommendedTracksGrid');
    if (!container) return;
    
    const recTracks = recommendedTracks.slice(0, 8);
    container.innerHTML = recTracks.map(track => createTrackCard(track)).join('');
    attachTrackCardListeners(container);
}

function renderRecommendedPlaylists() {
    const container = document.getElementById('recommendedPlaylistsGrid');
    if (!container) return;
    
    container.innerHTML = recommendedPlaylists.map(playlist => `
        <div class="playlist-card" data-playlist-id="${playlist.id}">
            <div class="playlist-card-art" style="background: linear-gradient(135deg, ${playlist.color}, ${playlist.color}cc);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                </svg>
            </div>
            <div class="playlist-name">${escapeHtml(playlist.name)}</div>
            <div class="playlist-count">${playlist.tracks} треков</div>
        </div>
    `).join('');
    
    container.querySelectorAll('.playlist-card').forEach(card => {
        card.addEventListener('click', () => {
            const playlistId = card.dataset.playlistId;
            const playlist = recommendedPlaylists.find(p => p.id === playlistId);
            if (playlist) {
                // Создаем временный плейлист для отображения
                const tempPlaylist = {
                    id: `rec_${playlistId}`,
                    name: playlist.name,
                    tracks: [...tracks.slice(0, playlist.tracks)]
                };
                switchToPlaylist(tempPlaylist);
            }
        });
    });
}

/**
 * Создает HTML-разметку для карточки трека.
 * @param {object} track - Объект трека.
 * @returns {string} HTML-строка.
 */
function createTrackCard(track) {
    return `
        <div class="home-track-card" data-track-id="${track.id}">
            <div class="track-card-art">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
                    <path d="M9 18V5l12-2v13" />
                    <circle cx="6" cy="18" r="3" />
                    <circle cx="18" cy="16" r="3" />
                </svg>
            </div>
            <div class="track-name">${escapeHtml(track.name)}</div>
            <div class="track-artist">${escapeHtml(track.artist)}</div>
        </div>
    `;
}

/**
 * Навешивает обработчики клика на все карточки треков внутри контейнера.
 * @param {HTMLElement} container - Родительский контейнер.
 */
function attachTrackCardListeners(container) {
    container.querySelectorAll('.home-track-card').forEach(card => {
        card.addEventListener('click', (e) => {
            e.stopPropagation();
            const trackId = parseInt(card.dataset.trackId);
            const track = tracks.find(t => t.id === trackId);
            if (track) openPlayer(track);
        });
    });
}