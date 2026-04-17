import { formatTime } from '../utils/helpers.js';

/**
 * Генерирует массив из 100 тестовых треков.
 * @returns {Array} Массив объектов треков.
 */
function generateTracks() {
    const totalTracks = 100;
    const startSeconds = 0;
    const endSeconds = 610; // 10 минут 10 секунд
    const step = (endSeconds - startSeconds) / (totalTracks - 1);
    const tracks = [];

    for (let i = 0; i < totalTracks; i++) {
        let timeSec = startSeconds + (i * step);
        if (i === totalTracks - 1) timeSec = endSeconds;
        
        const timeString = (i === 0 ? "0:00" : (i === totalTracks-1 ? "10:10" : formatTime(timeSec)));
        
        tracks.push({
            id: i,
            name: `New track ${i+1}`,
            album: "New album",
            duration: timeString,
            durationSeconds: timeSec,
            artist: `New artist ${Math.floor(i/10)+1}`,
            plays: Math.floor(Math.random() * 10000),
            addedDate: Date.now() - (i * 86400000) // Каждый трек добавлен на день раньше предыдущего
        });
    }
    return tracks;
}

export const tracks = generateTracks();

// Предсортированные версии для главной страницы
export const popularTracks = [...tracks].sort((a, b) => b.plays - a.plays);
export const newReleases = [...tracks].sort((a, b) => b.addedDate - a.addedDate);
export const recommendedTracks = [...tracks].sort(() => 0.5 - Math.random()).slice(0, 8);

// Данные для рекомендуемых плейлистов
export const recommendedPlaylists = [
    { id: 'focus', name: 'Focus Flow', tracks: 45, color: '#1e3a2a' },
    { id: 'chill', name: 'Chill Vibes', tracks: 62, color: '#2a3f5a' },
    { id: 'workout', name: 'Workout Mix', tracks: 38, color: '#5a3a2a' },
    { id: 'study', name: 'Study Session', tracks: 51, color: '#3a2a5a' },
    { id: 'party', name: 'Party Hits', tracks: 73, color: '#5a2a3a' },
    { id: 'sleep', name: 'Sleep Sounds', tracks: 29, color: '#2a5a3a' }
];

// Состояние пользовательских плейлистов
export let playlists = [
    { id: 'favorites', name: 'Любимые треки', tracks: [...tracks] },
    { id: 'playlist_1', name: 'Новый плейлист 1', tracks: [...tracks] }
];
export let nextPlaylistNumber = 2; // Счетчик для имен новых плейлистов
export const MAX_PLAYLISTS = 100;

// Функция для обновления состояния плейлистов (вызывается из ui модуля)
export function addPlaylist(newPlaylist) {
    playlists.push(newPlaylist);
}