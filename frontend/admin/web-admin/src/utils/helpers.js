import { formatPST } from "./dateUtils";

export function formatDateTime(date) {
    return formatPST(date);
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
