import { tracks } from '../data/data.js';
import { escapeHtml } from '../utils/helpers.js';

const favoritesContainer = document.getElementById('favoritesTracklist');

export function renderFavorites() {
    let html = '';
    tracks.forEach(track => {
        html += `
            <div class="track-item" data-track-id="${track.id}" data-source="favorites">
                <div class="track-container">
                    <div class="track-image">
                        <img src="images/pad.svg" alt="pad">
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
    favoritesContainer.innerHTML = html;
}