/**
 * Вспомогательные функции, используемые во всем приложении.
 */

/**
 * Форматирует количество секунд в строку вида "М:СС" (например, 65 -> "1:05").
 * @param {number} seconds - Количество секунд.
 * @returns {string} Отформатированное время.
 */
export function formatTime(seconds) {
    const totalSecs = Math.floor(seconds);
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${mins}:${secs < 10 ? '0' + secs : secs}`;
}

/**
 * Экранирует HTML-спецсимволы в строке для предотвращения XSS-атак.
 * @param {string} str - Строка для экранирования.
 * @returns {string} Экранированная строка.
 */
export function escapeHtml(str) {
    return String(str).replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

/**
 * Возвращает правильное склонение для слова "трек" в зависимости от числа.
 * @param {number} count - Количество треков.
 * @returns {string} Склонение ('', 'а', 'ов').
 */
export function getDeclension(count) {
    if (count % 10 === 1 && count % 100 !== 11) return '';
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return 'а';
    return 'ов';
}