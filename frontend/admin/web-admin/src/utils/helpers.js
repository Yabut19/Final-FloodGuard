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

/**
 * Compares two objects or values for deep equality.
 * Used to detect if form values have changed from their initial state.
 */
export function areValuesEqual(objA, objB) {
    // Handle primitive values
    if (objA === objB) return true;
    
    // Handle null/undefined
    if (!objA || !objB) return objA === objB;
    
    // Handle non-object types
    if (typeof objA !== 'object' || typeof objB !== 'object') return objA === objB;
    
    const keysA = Object.keys(objA);
    const keysB = Object.keys(objB);
    
    if (keysA.length !== keysB.length) return false;
    
    for (const key of keysA) {
        if (!keysB.includes(key)) return false;
        
        const valA = objA[key];
        const valB = objB[key];
        
        // Deep comparison for objects/arrays
        if (typeof valA === 'object' && valA !== null && typeof valB === 'object' && valB !== null) {
            if (!areValuesEqual(valA, valB)) return false;
        } else if (valA !== valB) {
            // Special handling for numbers vs strings (e.g. "200" vs 200)
            if (String(valA) !== String(valB)) {
                return false;
            }
        }
    }
    
    return true;
}
