import { supabase } from './supabaseClient'

// Read the backend URL from frontend/.env (defaults to http://localhost:8000)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Helper function to send authenticated requests to FastAPI.
 * It automatically grabs the Supabase JWT token and attaches it to the headers.
 */
async function request(endpoint, options = {}) {
    // 1. Get the current logged-in user's Supabase session
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token

    // 2. Prepare headers
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    }

    // 3. Make the actual HTTP call to FastAPI
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    })

    // 4. Handle errors (like 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation)
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        let errorMessage = `Request failed with status ${response.status}`
        if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail
        } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(e => `${e.loc ? e.loc[e.loc.length - 1] + ': ' : ''}${e.msg}`).join(', ')
        }
        throw new Error(errorMessage)
    }

    // 5. Return parsed JSON data
    return response.json()
}

// Export clean, easy-to-use functions for our app to call
export const api = {
    // Auth: Get current user profile and role from FastAPI (/auth/me)
    getMe: () => request('/auth/me'),

    // Categories & Departments
    getCategories: () => request('/categories'),
    getDepartments: () => request('/departments/'),

    // Grievances
    getGrievances: () => request('/grievances'),
    getGrievanceById: (id) => request(`/grievances/${id}`),
    createGrievance: (data) => request('/grievances', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    updateGrievance: (id, data) => request(`/grievances/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),

    // Grievance Audit Updates
    getGrievanceUpdates: (grievanceId) => request(`/grievance-updates/grievance/${grievanceId}`),
    addGrievanceUpdate: (data) => request('/grievance-updates', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
}
