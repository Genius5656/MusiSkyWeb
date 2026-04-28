import { playlists, addPlaylist, nextPlaylistNumber, MAX_PLAYLISTS, tracks } from '../data/data.js';
import { switchToPlaylist, playlistsContainer, playlistPagesContainer } from './ui.js';
import { escapeHtml } from '../utils/helpers.js';

export function renderPlaylistPage(playlist) {
    const pageId = `playlist_${playlist.id}`;
    let page = document.getElementById(pageId);
    
    if (!page) {
        page = document.createElement('div');
        page.id = pageId;
        page.className = 'playlist-page';
        playlistPagesContainer.appendChild(page);
    }
    
    const totalDuration = playlist.tracks.reduce((sum, track) => sum + track.durationSeconds, 0);
    const totalHours = Math.floor(totalDuration / 3600);
    const totalMinutes = Math.floor((totalDuration / 60) % 60);
    const totalSeconds = Math.floor(totalDuration % 60);
    const totalTimeString = `${totalHours}:${totalMinutes}:${totalSeconds}`;
    
    page.innerHTML = `
        <div class="playlist-header">
            <div class="title-section">
                <div class="title-badge">
                    <h1>${escapeHtml(playlist.name)}</h1>
                    <img src="images/edit-playlist.svg" alt="edit">
                </div>
                <p>Коллекция избранной музыки · ${playlist.tracks.length} треков · ${totalTimeString} минут</p>
            </div>
            <div class="edit-buttons">
                <div class="edit-button" style="padding: 10px 21px;">
                    <img src="images/reverse.svg" alt="mix" width="20px" height="15px">
                    <span style="margin-top: -2px;">Перемешать</span>
                </div>
                <div class="edit-button" style="padding-top: 12px;">
                    <img src="images/edit-tracks.svg" alt="edit" width="20px" height="15px">
                    <span style="margin-top: -5px;">Редактировать</span>
                </div>
            </div>
        </div>
        <div class="tracklist" id="playlist_tracklist_${playlist.id}"></div>
        <div class="extra-row">
            <div class="extra-badge">
                <img src="images/music_note.svg" alt="note" width="22" height="22" style="filter: invert(0.7);">
                <span class="extra-text">New track</span>
            </div>
            <div class="extra-badge">
                <img src="images/performance.svg" alt="performance" width="22" height="22" style="filter: invert(0.7);">
                <span class="extra-text">New performance</span>
            </div>
            <div class="extra-badge">
                <img src="images/album.svg" alt="album" width="22" height="22" style="filter: invert(0.7);">
                <span class="extra-text">New album</span>
            </div>
        </div>
        <div class="tracklist-note">
            🎶 ${playlist.tracks.length} треков · полный хронометраж 0:00 – ${totalTimeString} · нажми на любую песню, чтобы открыть плеер
        </div>
    `;
    
    const tracklistContainer = document.getElementById(`playlist_tracklist_${playlist.id}`);
    renderPlaylistTracks(tracklistContainer, playlist.tracks);
    
    return page;
}

function renderPlaylistTracks(container, tracksList) {
    let html = '';
    tracksList.forEach(track => {
        html += `
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
    container.innerHTML = html;
}

// --- Управление созданием плейлистов ---

export function createPlaylistButton(playlist) {
    const button = document.createElement('button');
    button.className = 'nav-item';
    button.setAttribute('data-playlist-id', playlist.id);
    button.type = 'button';
    button.innerHTML = `
        <img class="image" src="images/pen.svg" alt="playlist icon" width="20" height="20">
        <span>${escapeHtml(playlist.name)}</span>
    `;
    button.addEventListener('click', () => switchToPlaylist(playlist));
    return button;
}

export function addNewPlaylist() {
    if (playlists.length >= MAX_PLAYLISTS) {
        alert(`Достигнуто максимальное количество плейлистов (${MAX_PLAYLISTS})`);
        return;
    }
    
    const playlistName = `Новый плейлист ${playlists.length}`;
    const playlistId = `playlist_${Date.now()}`;
    
    const newPlaylist = { id: playlistId, name: playlistName, tracks: [...tracks] };
    addPlaylist(newPlaylist);
    
    const button = createPlaylistButton(newPlaylist);
    playlistsContainer.appendChild(button);
    
    // nextPlaylistNumber увеличится в data.js, но мы можем просто обновить здесь
    // nextPlaylistNumber++;
    
    setTimeout(() => button.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);
}

export function renderExistingPlaylists() {
    const existingButtons = playlistsContainer.querySelectorAll('.nav-item[data-playlist-id]');
    existingButtons.forEach(btn => btn.remove());
    
    playlists.forEach(playlist => {
        if (playlist.id !== 'favorites') {
            const button = createPlaylistButton(playlist);
            playlistsContainer.appendChild(button);
        }
    });
}