/**
 * Centralized API helper module
 */
const API = {
    async request(endpoint, options = {}) {
        options.headers = options.headers || {};
        
        // If sending JSON body, set Content-Type
        if (options.body && !(options.body instanceof FormData)) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(endpoint, options);
            const data = await response.json().catch(() => ({}));

            if (response.status === 401) {
                // If unauthorized on a protected page, redirect to login
                if (!window.location.pathname.includes("/login") && !window.location.pathname.includes("/register")) {
                    window.location.href = "/login";
                }
            }

            return {
                ok: response.ok,
                status: response.status,
                data: data
            };
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            return {
                ok: false,
                status: 0,
                data: { error: "Network or server connection error." }
            };
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: "GET" });
    },

    post(endpoint, body) {
        return this.request(endpoint, { method: "POST", body });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: "DELETE" });
    }
};
