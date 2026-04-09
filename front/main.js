(function() {
    // Генерируем 100 треков
    const totalTracks = 100;
    const startSeconds = 0;
    const endSeconds = 610;
    const step = (endSeconds - startSeconds) / (totalTracks - 1);
    
    function formatTime(seconds) {
        const totalSecs = Math.floor(seconds);
        const mins = Math.floor(totalSecs / 60);
        const secs = totalSecs % 60;
        return `${mins}:${secs < 10 ? '0' + secs : secs}`;
    }
    
    const tracks = [];
    for (let i = 0; i < totalTracks; i++) {
        let timeSec = startSeconds + (i * step);
        if (i === totalTracks - 1) timeSec = endSeconds;
        const timeString = (i === 0 ? "0:00" : (i === totalTracks-1 ? "10:10" : formatTime(timeSec)));
        
        const trackName = `New track ${i+1}`;
        const artistName = `New artist ${Math.floor(i/10)+1}`;
        tracks.push({
            id: i,
            name: trackName,
            album: "New album",
            duration: timeString,
            durationSeconds: timeSec,
            artist: artistName,
            plays: Math.floor(Math.random() * 10000),
            addedDate: Date.now() - (i * 86400000)
        });
    }
    
    // Сортируем треки по популярности
    const popularTracks = [...tracks].sort((a, b) => b.plays - a.plays);
    const newReleases = [...tracks].sort((a, b) => b.addedDate - a.addedDate);
    const recommendedTracks = [...tracks].sort(() => 0.5 - Math.random()).slice(0, 8);
    
    // Рекомендуемые плейлисты
    const recommendedPlaylists = [
        { id: 'focus', name: 'Focus Flow', tracks: 45, color: '#1e3a2a' },
        { id: 'chill', name: 'Chill Vibes', tracks: 62, color: '#2a3f5a' },
        { id: 'workout', name: 'Workout Mix', tracks: 38, color: '#5a3a2a' },
        { id: 'study', name: 'Study Session', tracks: 51, color: '#3a2a5a' },
        { id: 'party', name: 'Party Hits', tracks: 73, color: '#5a2a3a' },
        { id: 'sleep', name: 'Sleep Sounds', tracks: 29, color: '#2a5a3a' }
    ];
    
    // Хранилище для плейлистов
    let playlists = [
        { id: 'favorites', name: 'Любимые треки', tracks: [...tracks] },
        { id: 'playlist_1', name: 'Новый плейлист 1', tracks: [...tracks] }
    ];
    
    let nextPlaylistNumber = 2;
    const MAX_PLAYLISTS = 100;
    
    // DOM элементы
    const mainContent = document.getElementById('mainContent');
    const homePage = document.getElementById('homePage');
    const favoritesPage = document.getElementById('favoritesPage');
    const searchPage = document.getElementById('searchPage');
    const homeNavBtn = document.querySelector('.nav-item:first-child');
    const searchNavBtn = document.getElementById('searchNavBtn');
    const favoritesBtn = document.getElementById('favoritesBtn');
    const playlistsContainer = document.getElementById('playlistsContainer');
    const createPlaylistBtn = document.getElementById('createPlaylistBtn');
    
    // Контейнер для динамических страниц плейлистов
    let playlistPagesContainer = null;
    
    function initPlaylistPagesContainer() {
        if (!playlistPagesContainer) {
            playlistPagesContainer = document.createElement('div');
            playlistPagesContainer.id = 'playlistPagesContainer';
            mainContent.appendChild(playlistPagesContainer);
        }
    }
    
    function renderPlaylistPage(playlist) {
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
                    <img src="../images/music_note.svg" alt="note" width="22" height="22" style="filter: invert(0.7);">
                    <span class="extra-text">New track</span>
                </div>
                <div class="extra-badge">
                    <img src="../images/performance.svg" alt="performance" width="22" height="22" style="filter: invert(0.7);">
                    <span class="extra-text">New performance</span>
                </div>
                <div class="extra-badge">
                    <img src="../images/album.svg" alt="album" width="22" height="22" style="filter: invert(0.7);">
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
    
    function switchToHome() {
        // Скрываем все страницы
        favoritesPage.classList.remove('active-page');
        searchPage.classList.remove('active-page');
        document.querySelectorAll('.playlist-page').forEach(page => {
            page.classList.remove('active-page');
        });
        
        // Показываем главную страницу
        homePage.classList.add('active-page');
        
        // Обновляем активные кнопки в меню
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (homeNavBtn) homeNavBtn.classList.add('active');
        favoritesBtn.classList.remove('active');
        searchNavBtn.classList.remove('active');
        
        closePlayerIfNeeded();
        renderHomeContent();
    }
    
    function switchToPlaylist(playlist) {
        // Скрываем все страницы
        favoritesPage.classList.remove('active-page');
        searchPage.classList.remove('active-page');
        homePage.classList.remove('active-page');
        document.querySelectorAll('.playlist-page').forEach(page => {
            page.classList.remove('active-page');
        });
        
        // Показываем страницу плейлиста
        const page = renderPlaylistPage(playlist);
        page.classList.add('active-page');
        
        // Обновляем активные кнопки в меню
        document.querySelectorAll('.nav-item').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const playlistBtn = document.querySelector(`.nav-item[data-playlist-id="${playlist.id}"]`);
        if (playlistBtn) playlistBtn.classList.add('active');
        
        favoritesBtn.classList.remove('active');
        searchNavBtn.classList.remove('active');
        if (homeNavBtn) homeNavBtn.classList.remove('active');
        
        closePlayerIfNeeded();
    }
    
    function switchToPage(pageName) {
        favoritesPage.classList.remove('active-page');
        searchPage.classList.remove('active-page');
        homePage.classList.remove('active-page');
        document.querySelectorAll('.playlist-page').forEach(page => {
            page.classList.remove('active-page');
        });
        
        if (pageName === 'home') {
            homePage.classList.add('active-page');
            if (homeNavBtn) homeNavBtn.classList.add('active');
            favoritesBtn.classList.remove('active');
            searchNavBtn.classList.remove('active');
            document.querySelectorAll('.nav-item[data-playlist-id]').forEach(btn => {
                btn.classList.remove('active');
            });
            renderHomeContent();
        } else if (pageName === 'favorites') {
            favoritesPage.classList.add('active-page');
            favoritesBtn.classList.add('active');
            if (homeNavBtn) homeNavBtn.classList.remove('active');
            searchNavBtn.classList.remove('active');
            document.querySelectorAll('.nav-item[data-playlist-id]').forEach(btn => {
                btn.classList.remove('active');
            });
        } else if (pageName === 'search') {
            searchPage.classList.add('active-page');
            searchNavBtn.classList.add('active');
            if (homeNavBtn) homeNavBtn.classList.remove('active');
            favoritesBtn.classList.remove('active');
            document.querySelectorAll('.nav-item[data-playlist-id]').forEach(btn => {
                btn.classList.remove('active');
            });
            setTimeout(() => {
                searchInput.focus();
            }, 100);
        }
    }
    
    function renderHomeContent() {
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
        container.innerHTML = topTracks.map(track => `
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
        `).join('');
        
        container.querySelectorAll('.home-track-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.stopPropagation();
                const trackId = parseInt(card.dataset.trackId);
                const track = tracks.find(t => t.id === trackId);
                if (track) openPlayer(track);
            });
        });
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
                    // Создаем временный плейлист
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
    
    function renderNewReleases() {
        const container = document.getElementById('newReleasesGrid');
        if (!container) return;
        
        const newTracks = newReleases.slice(0, 8);
        container.innerHTML = newTracks.map(track => `
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
        `).join('');
        
        container.querySelectorAll('.home-track-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.stopPropagation();
                const trackId = parseInt(card.dataset.trackId);
                const track = tracks.find(t => t.id === trackId);
                if (track) openPlayer(track);
            });
        });
    }
    
    function renderRecommendedTracks() {
        const container = document.getElementById('recommendedTracksGrid');
        if (!container) return;
        
        const recTracks = recommendedTracks.slice(0, 8);
        container.innerHTML = recTracks.map(track => `
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
        `).join('');
        
        container.querySelectorAll('.home-track-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.stopPropagation();
                const trackId = parseInt(card.dataset.trackId);
                const track = tracks.find(t => t.id === trackId);
                if (track) openPlayer(track);
            });
        });
    }
    
    function createPlaylistButton(playlist) {
        const button = document.createElement('button');
        button.className = 'nav-item';
        button.setAttribute('data-playlist-id', playlist.id);
        button.type = 'button';
        button.innerHTML = `
            <img class="image" src="images/pen.svg" alt="playlist icon" width="20" height="20">
            <span>${escapeHtml(playlist.name)}</span>
        `;
        
        button.addEventListener('click', () => {
            switchToPlaylist(playlist);
        });
        
        return button;
    }
    
    function addNewPlaylist() {
        if (playlists.length >= MAX_PLAYLISTS) {
            alert(`Достигнуто максимальное количество плейлистов (${MAX_PLAYLISTS})`);
            return;
        }
        
        const playlistName = `Новый плейлист ${nextPlaylistNumber}`;
        const playlistId = `playlist_${Date.now()}`;
        
        const newPlaylist = {
            id: playlistId,
            name: playlistName,
            tracks: [...tracks]
        };
        
        playlists.push(newPlaylist);
        
        const button = createPlaylistButton(newPlaylist);
        playlistsContainer.appendChild(button);
        
        nextPlaylistNumber++;
        
        setTimeout(() => {
            button.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }
    
    function renderExistingPlaylists() {
        const existingButtons = playlistsContainer.querySelectorAll('.nav-item[data-playlist-id]');
        existingButtons.forEach(btn => btn.remove());
        
        playlists.forEach(playlist => {
            if (playlist.id !== 'favorites') {
                const button = createPlaylistButton(playlist);
                playlistsContainer.appendChild(button);
            }
        });
        
        const maxNumber = Math.max(...playlists
            .filter(p => p.name.startsWith('Новый плейлист '))
            .map(p => parseInt(p.name.replace('Новый плейлист ', '')))
            .filter(n => !isNaN(n)), 0);
        nextPlaylistNumber = maxNumber + 1;
    }
    
    const favoritesContainer = document.getElementById('favoritesTracklist');
    function renderFavorites() {
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
    
    const searchInput = document.getElementById('searchInput');
    const searchResultsContainer = document.getElementById('searchResultsList');
    const searchStats = document.getElementById('searchStats');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    
    let currentSearchQuery = '';
    
    function performSearch() {
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
    
    function getDeclension(count) {
        if (count % 10 === 1 && count % 100 !== 11) return '';
        if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return 'а';
        return 'ов';
    }
    
    function escapeHtml(str) {
        return String(str).replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }
    
    function clearSearch() {
        searchInput.value = '';
        performSearch();
        searchInput.focus();
    }
    
    // Навигация между страницами
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
        performSearch();
    });
    
    createPlaylistBtn.addEventListener('click', addNewPlaylist);
    
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
                setTimeout(() => {
                    searchInput.value = 'New track';
                    performSearch();
                }, 100);
            }
        }
        
        const seeAllBtn = e.target.closest('.see-all-btn');
        if (seeAllBtn) {
            const section = seeAllBtn.dataset.section;
            switchToPage('search');
            if (section === 'popular') {
                setTimeout(() => {
                    searchInput.value = 'New track';
                    performSearch();
                }, 100);
            }
        }
    });
    
    // Модальное окно
    const registerModal = document.getElementById('registerModal');
    let isRegistered = false;

    // Получаем элементы форм
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const modalTitle = document.getElementById('modalTitle');

    // Функции открытия/закрытия модального окна
    function openRegisterModal() {
        registerModal.style.display = 'block';
        // По умолчанию показываем форму регистрации
        showRegisterForm();
    }

    function closeRegisterModal() {
        registerModal.style.display = 'none';
        // Очищаем ошибки при закрытии
        clearErrors();
    }

    // Функция показа формы регистрации
    function showRegisterForm() {
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
        modalTitle.textContent = 'Регистрация';
        clearErrors();
    }

    // Функция показа формы авторизации
    function showLoginForm() {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        modalTitle.textContent = 'Авторизация';
        clearErrors();
    }

    // Очистка сообщений об ошибках
    function clearErrors() {
        document.getElementById('registerError').textContent = '';
        document.getElementById('loginError').textContent = '';
        // Очищаем поля ввода
        document.getElementById('regUsername').value = '';
        document.getElementById('regEmail').value = '';
        document.getElementById('regPassword').value = '';
        document.getElementById('confirmPassword').value = '';
        document.getElementById('loginEmail').value = '';
        document.getElementById('loginPassword').value = '';
    }

    // Валидация пароля
    function validatePassword(password, confirmPassword) {
        if (password !== confirmPassword) {
            return 'Пароли не совпадают';
        }
        if (password.length < 6) {
            return 'Пароль должен содержать минимум 6 символов';
        }
        return null;
    }

    // Обработка регистрации
    registerForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const username = document.getElementById('regUsername').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const errorElement = document.getElementById('registerError');
        
        // Валидация имени
        if (!username) {
            errorElement.textContent = 'Введите имя пользователя';
            return;
        }
        
        // Валидация email
        if (!email || !email.includes('@')) {
            errorElement.textContent = 'Введите корректный email';
            return;
        }
        
        // Валидация пароля
        const passwordError = validatePassword(password, confirmPassword);
        if (passwordError) {
            errorElement.textContent = passwordError;
            return;
        }
        
        // Проверка, существует ли пользователь
        const existingUser = localStorage.getItem(`user_${email}`);
        if (existingUser) {
            errorElement.textContent = 'Пользователь с таким email уже существует';
            return;
        }
        
        // Сохраняем данные пользователя
        const userData = { 
            username, 
            email, 
            password: btoa(password),
            registeredAt: new Date().toISOString()
        };
        
        localStorage.setItem(`user_${email}`, JSON.stringify(userData));
        localStorage.setItem('currentUser', JSON.stringify({ username, email }));
        isRegistered = true;
        
        errorElement.textContent = '';
        alert(`Добро пожаловать, ${username}! Регистрация успешно завершена.`);
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
        
        // Валидация email
        if (!email || !email.includes('@')) {
            errorElement.textContent = 'Введите корректный email';
            return;
        }
        
        // Валидация пароля
        if (!password) {
            errorElement.textContent = 'Введите пароль';
            return;
        }
        
        // Получаем данные пользователя
        const userDataStr = localStorage.getItem(`user_${email}`);
        
        if (!userDataStr) {
            errorElement.textContent = 'Пользователь с таким email не найден';
            return;
        }
        
        try {
            const userData = JSON.parse(userDataStr);
            
            // Проверяем пароль
            if (btoa(password) !== userData.password) {
                errorElement.textContent = 'Неверный пароль';
                return;
            }
            
            // Успешный вход
            errorElement.textContent = '';
            localStorage.setItem('currentUser', JSON.stringify({ 
                username: userData.username, 
                email: userData.email 
            }));
            
            alert(`С возвращением, ${userData.username}!`);
            closeRegisterModal();
            updateProfileButton(userData.username);
            updateGreeting();
        } catch (e) {
            errorElement.textContent = 'Ошибка при входе. Попробуйте снова.';
            console.error('Login error:', e);
        }
    });

    // Обновление кнопки профиля
    function updateProfileButton(username) {
        const profileBtn = document.querySelector('.profile-btn');
        if (profileBtn) {
            profileBtn.innerHTML = `<img src="images/user.svg" alt="user" width="16" height="16" style="opacity:0.6; margin-right: 6px;"> ${username}`;
        }
    }

    // Обновление приветствия 
    function updateGreeting() {
        const greetingSpan = document.getElementById('userGreeting');
        if (greetingSpan) {
            const userData = localStorage.getItem('currentUser');
            if (userData) {
                try {
                    const user = JSON.parse(userData);
                    greetingSpan.textContent = user.username || 'Гость';
                } catch(e) {
                    greetingSpan.textContent = 'Гость';
                }
            } else {
                greetingSpan.textContent = 'Гость';
            }
        }
    }

    // Переключение между формами
    document.getElementById('switchToLogin')?.addEventListener('click', showLoginForm);
    document.getElementById('switchToRegister')?.addEventListener('click', showRegisterForm);

    // Закрытие модального окна
    document.querySelector('.modal-close')?.addEventListener('click', closeRegisterModal);
    window.addEventListener('click', (e) => {
        if (e.target === registerModal) closeRegisterModal();
    });

    // Инициализация кнопки профиля
    const profileBtn = document.querySelector('.profile-btn');
    if (profileBtn) {
        profileBtn.addEventListener('click', openRegisterModal);
        
        // Проверяем, есть ли активная сессия
        const currentUser = localStorage.getItem('currentUser');
        if (currentUser) {
            try {
                const user = JSON.parse(currentUser);
                profileBtn.innerHTML = `<img src="images/user.svg" alt="user" width="16" height="16" style="opacity:0.6; margin-right: 6px;"> ${user.username}`;
            } catch(e) {
                console.error('Error loading user data:', e);
            }
        }
    }

    // При загрузке страницы проверяем активную сессию
    document.addEventListener('DOMContentLoaded', () => {
        const currentUser = localStorage.getItem('currentUser');
        if (currentUser) {
            try {
                const user = JSON.parse(currentUser);
                updateProfileButton(user.username);
            } catch(e) {}
        }
    });
    
    // ПЛЕЕР ЛОГИКА
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
    
    let currentTrack = null;
    let isPlaying = false;
    let playInterval = null;
    let currentProgressSeconds = 0;
    
    function stopPlaybackSimulation() {
        if (playInterval) {
            clearInterval(playInterval);
            playInterval = null;
        }
        isPlaying = false;
        if (playPauseBtn) playPauseImg.src = 'images/play.svg';
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
                playNextTrack();
            }
        }, 500);
        isPlaying = true;
        if (playPauseBtn) playPauseImg.src = 'images/pause.svg';
    }
    
    function updateProgressDisplay(currentSec, totalSec) {
        const minsCurr = Math.floor(currentSec / 60);
        const secsCurr = Math.floor(currentSec % 60);
        const minsTotal = Math.floor(totalSec / 60);
        const secsTotal = Math.floor(totalSec % 60);
        currentTimeSpan.textContent = `${minsCurr}:${secsCurr < 10 ? '0' + secsCurr : secsCurr}`;
        totalTimeSpan.textContent = `${minsTotal}:${secsTotal < 10 ? '0' + secsTotal : secsTotal}`;
        const percent = (currentSec / totalSec) * 100;
        progressFill.style.width = `${percent}%`;
    }
    
    function openPlayer(track) {
        if (!track) return;
        currentTrack = track;
        
        playerTrackNameSpan.textContent = track.name;
        playerArtistSpan.textContent = track.artist;
        playerAlbumDetailSpan.textContent = track.album || "New album";
        
        let durationSeconds = track.durationSeconds;
        if (!durationSeconds && track.duration) {
            const parts = track.duration.split(':');
            if (parts.length === 2) {
                durationSeconds = parseInt(parts[0]) * 60 + parseInt(parts[1]);
            } else {
                durationSeconds = 30;
            }
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
    
    function closePlayerIfNeeded() {
        if (playerPanel.classList.contains('open')) {
            playerPanel.classList.remove('open');
            mainContent.classList.remove('player-open');
            stopPlaybackSimulation();
            currentTrack = null;
        }
    }
    
    function closePlayer() {
        closePlayerIfNeeded();
    }
    
    function playNextTrack() {
        if (!currentTrack) return;
        const currentIndex = tracks.findIndex(t => t.id === currentTrack.id);
        let nextIndex = currentIndex + 1;
        if (nextIndex >= tracks.length) nextIndex = 0;
        const nextTrack = tracks[nextIndex];
        if (nextTrack) openPlayer(nextTrack);
    }
    
    function playPrevTrack() {
        if (!currentTrack) return;
        const currentIndex = tracks.findIndex(t => t.id === currentTrack.id);
        let prevIndex = currentIndex - 1;
        if (prevIndex < 0) prevIndex = tracks.length - 1;
        const prevTrack = tracks[prevIndex];
        if (prevTrack) openPlayer(prevTrack);
    }
    
    function togglePlayPause() {
        if (!currentTrack) return;
        if (isPlaying) {
            if (playInterval) {
                clearInterval(playInterval);
                playInterval = null;
            }
            isPlaying = false;
            playPauseImg.src = 'images/play.svg';
        } else {
            let durationSec = currentTrack.durationSeconds;
            if (!durationSec && currentTrack.duration) {
                const parts = currentTrack.duration.split(':');
                durationSec = parseInt(parts[0]) * 60 + parseInt(parts[1]);
            }
            if (currentProgressSeconds >= durationSec) currentProgressSeconds = 0;
            startPlaybackSimulation(durationSec);
        }
    }
    
    document.addEventListener('click', (e) => {
        const trackDiv = e.target.closest('.track-item');
        if (trackDiv) {
            const trackId = parseInt(trackDiv.dataset.trackId);
            const selectedTrack = tracks.find(t => t.id === trackId);
            if (selectedTrack) {
                openPlayer(selectedTrack);
            }
        }
    });
    
    closeBtn.addEventListener('click', closePlayer);
    playPauseBtn.addEventListener('click', togglePlayPause);
    nextBtn.addEventListener('click', () => {
        if (currentTrack) playNextTrack();
        else if (tracks.length) openPlayer(tracks[0]);
    });
    prevBtn.addEventListener('click', () => {
        if (currentTrack) playPrevTrack();
        else if (tracks.length) openPlayer(tracks[0]);
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && playerPanel.classList.contains('open')) {
            closePlayer();
        }
    });
    
    // Инициализация
    initPlaylistPagesContainer();
    renderFavorites();
    performSearch();
    renderExistingPlaylists();
    renderHomeContent();
    
    // Открываем страницу "Домой" по умолчанию
    switchToPage('home');
    
    console.log(`Готово: ${tracks.length} треков, зеленая тема активна`);
})();