export function formatDateTime(date) {
    const optionsDate = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
    const optionsTime = { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false };
    const dateStr = date.toLocaleDateString(undefined, optionsDate);
    const timeStr = date.toLocaleTimeString(undefined, optionsTime);
    return `${dateStr} • ${timeStr}`;
}

/**
 * Wrapper around fetch() that automatically attaches the JWT
 * Authorization header from localStorage.
 *
 * Usage: replace `fetch(url, options)` with `authFetch(url, options)`
 * for any request that requires authentication.
 */
export function authFetch(url, options = {}) {
    const token = localStorage.getItem("authToken");
    const headers = {
        ...(options.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    return fetch(url, { ...options, headers });
}
