import { tracks } from '../data/data.js';

// --- DOM Элементы плеера ---
const playerPanel = document.getElementById('playerPanel');
const closeBtn = document.getElementById('closePlayerBtn');
const playerTrackNameSpan = document.getElementById('playerTrackName');
const playerArtistSpan = document.getElementById('playerArtist');
const playerAlbumDetailSpan = document.getElementById('playerAlbumDetail');
const totalTimeSpan = document.getElementById('totalTimeDisplay');
const currentTimeSpan = document.getElementById('currentTimeDisplay');
const progressFill = document.getElementById('progressFill');
const playPauseBtn = document.getElementById('playPauseBtn');
const playPauseImg = document.getElementById('playPauseImg');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const mainContent = document.getElementById('mainContent');

// Состояние плеера
let currentTrack = null;
let isPlaying = false;
let playInterval = null;
let currentProgressSeconds = 0;

// --- Внутренние функции управления плеером ---

function stopPlaybackSimulation() {
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
    }
    isPlaying = false;
    if (playPauseBtn) playPauseImg.src = 'images/play.svg';
}

function updateProgressDisplay(currentSec, totalSec) {
    const minsCurr = Math.floor(currentSec / 60);
    const secsCurr = Math.floor(currentSec % 60);
    const minsTotal = Math.floor(totalSec / 60);
    const secsTotal = Math.floor(totalSec % 60);
    currentTimeSpan.textContent = `${minsCurr}:${secsCurr < 10 ? '0' + secsCurr : secsCurr}`;
    totalTimeSpan.textContent = `${minsTotal}:${secsTotal < 10 ? '0' + secsTotal : secsTotal}`;
    const percent = totalSec > 0 ? (currentSec / totalSec) * 100 : 0;
    progressFill.style.width = `${percent}%`;
}

function startPlaybackSimulation(durationSec) {
    if (playInterval) stopPlaybackSimulation();
    if (!currentTrack) return;
    
    currentProgressSeconds = 0;
    updateProgressDisplay(0, durationSec);
    
    playInterval = setInterval(() => {
        if (currentProgressSeconds < durationSec) {
            currentProgressSeconds += 0.5;
            if (currentProgressSeconds > durationSec) currentProgressSeconds = durationSec;
            updateProgressDisplay(currentProgressSeconds, durationSec);
        }
        if (currentProgressSeconds >= durationSec) {
            stopPlaybackSimulation();
            playNextTrack(); // Автоматически следующий трек
        }
    }, 500);
    isPlaying = true;
    if (playPauseBtn) playPauseImg.src = 'images/pause.svg';
}

// --- Публичные функции плеера ---

/**
 * Открывает плеер и начинает воспроизведение выбранного трека.
 * @param {object} track - Объект трека для воспроизведения.
 */
export function openPlayer(track) {
    if (!track) return;
    currentTrack = track;
    
    playerTrackNameSpan.textContent = track.name;
    playerArtistSpan.textContent = track.artist;
    playerAlbumDetailSpan.textContent = track.album || "New album";
    
    let durationSeconds = track.durationSeconds;
    if (!durationSeconds && track.duration) {
        const parts = track.duration.split(':');
        durationSeconds = parts.length === 2 ? parseInt(parts[0]) * 60 + parseInt(parts[1]) : 30;
    }
    if (!durationSeconds) durationSeconds = 30;
    
    totalTimeSpan.textContent = track.duration;
    currentTimeSpan.textContent = "0:00";
    progressFill.style.width = "0%";
    
    stopPlaybackSimulation();
    currentProgressSeconds = 0;
    updateProgressDisplay(0, durationSeconds);
    
    if (!playerPanel.classList.contains('open')) {
        playerPanel.classList.add('open');
        mainContent.classList.add('player-open');
    }
    
    startPlaybackSimulation(durationSeconds);
}

export function closePlayerIfNeeded() {
    if (playerPanel.classList.contains('open')) {
        playerPanel.classList.remove('open');
        mainContent.classList.remove('player-open');
        stopPlaybackSimulation();
        currentTrack = null;
    }
}

export function closePlayer() {
    closePlayerIfNeeded();
}

export function togglePlayPause() {
    if (!currentTrack) return;
    if (isPlaying) {
        stopPlaybackSimulation();
    } else {
        let durationSec = currentTrack.durationSeconds;
        if (!durationSec && currentTrack.duration) {
            const parts = currentTrack.duration.split(':');
            durationSec = parts.length === 2 ? parseInt(parts[0]) * 60 + parseInt(parts[1]) : 30;
        }
        if (currentProgressSeconds >= durationSec) currentProgressSeconds = 0;
        startPlaybackSimulation(durationSec);
    }
}

export function playNextTrack() {
    if (!currentTrack) return;
    const currentIndex = tracks.findIndex(t => t.id === currentTrack.id);
    const nextIndex = (currentIndex + 1) % tracks.length;
    openPlayer(tracks[nextIndex]);
}

export function playPrevTrack() {
    if (!currentTrack) return;
    const currentIndex = tracks.findIndex(t => t.id === currentTrack.id);
    const prevIndex = (currentIndex - 1 + tracks.length) % tracks.length;
    openPlayer(tracks[prevIndex]);
}

// --- Инициализация слушателей плеера (вызывается из app.js) ---
export function initPlayer() {
    closeBtn.addEventListener('click', closePlayer);
    playPauseBtn.addEventListener('click', togglePlayPause);
    nextBtn.addEventListener('click', () => currentTrack ? playNextTrack() : openPlayer(tracks[0]));
    prevBtn.addEventListener('click', () => currentTrack ? playPrevTrack() : openPlayer(tracks[0]));
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && playerPanel.classList.contains('open')) {
            closePlayer();
        }
    });
    
    // Глобальный слушатель для кликов по трекам
    document.addEventListener('click', (e) => {
        const trackDiv = e.target.closest('.track-item');
        if (trackDiv) {
            const trackId = parseInt(trackDiv.dataset.trackId);
            const selectedTrack = tracks.find(t => t.id === trackId);
            if (selectedTrack) openPlayer(selectedTrack);
        }
    });
}