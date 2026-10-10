import React, { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import { api } from './api'
import { IconAlertCircle } from './components/Icons'
import Navbar from './components/Navbar'
import AuthView from './components/AuthView'
import StudentDashboard from './components/StudentDashboard'
import StaffDashboard from './components/StaffDashboard'

export default function App() {
  const [session, setSession] = useState(null)
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // For Admin role: ability to preview either view
  const [adminViewMode, setAdminViewMode] = useState('admin') // 'admin' or 'student'

  useEffect(() => {
    // 1. Check initial Supabase session on app launch
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session) {
        loadUserProfile()
      } else {
        setLoading(false)
      }
    })

    // 2. Listen for auth changes (sign in, sign out, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      if (session) {
        loadUserProfile()
      } else {
        setCurrentUser(null)
        setLoading(false)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const loadUserProfile = async () => {
    setLoading(true)
    setError(null)
    try {
      // Call FastAPI backend GET /auth/me to get user record & role
      const profile = await api.getMe()
      setCurrentUser(profile)
    } catch (err) {
      console.error('Failed to load user profile from backend:', err)
      setError('Could not connect to FastAPI backend. Ensure backend server is running on http://localhost:8000.')
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = () => {
    setSession(null)
    setCurrentUser(null)
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="brand-icon">SG</div>
        <div className="spinner"></div>
        <p className="loading-text">Loading...</p>
      </div>
    )
  }

  return (
    <div className="app-container">
      <Navbar user={currentUser} onSignOut={handleSignOut} />

      <main className="main-content">
        {/* If backend is unreachable, show clear alert */}
        {error && (
          <div className="alert alert-error mb-4">
            <IconAlertCircle className="alert-icon" />
            <div style={{ flex: 1 }}>
              <strong>Backend Connection Issue</strong>
              <div className="text-xs mt-1">{error}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--gray-500)' }}>
                Start the backend with: <code>uvicorn app.main:app --reload</code>
              </div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={loadUserProfile}>
              Retry
            </button>
          </div>
        )}

        {/* 1. Not Authenticated -> Show Auth (Login / Register) */}
        {!session || !currentUser ? (
          <AuthView onAuthSuccess={() => loadUserProfile()} />
        ) : (
          /* 2. Authenticated -> Show Dashboard based on Role */
          <div>
            {/* Admin Switcher Bar (only for admins) */}
            {currentUser.role === 'admin' && (
              <div className="view-toggle-bar">
                <span className="view-toggle-label">View:</span>
                <div className="view-toggle">
                  <button
                    className={`btn btn-sm ${adminViewMode === 'admin' ? 'btn-primary' : 'btn-ghost'}`}
                    style={{ border: 'none' }}
                    onClick={() => setAdminViewMode('admin')}
                  >
                    Staff Queue
                  </button>
                  <button
                    className={`btn btn-sm ${adminViewMode === 'student' ? 'btn-primary' : 'btn-ghost'}`}
                    style={{ border: 'none' }}
                    onClick={() => setAdminViewMode('student')}
                  >
                    Student View
                  </button>
                </div>
              </div>
            )}

            {/* Render appropriate dashboard */}
            {currentUser.role === 'student' || (currentUser.role === 'admin' && adminViewMode === 'student') ? (
              <StudentDashboard user={currentUser} />
            ) : (
              <StaffDashboard user={currentUser} />
            )}
          </div>
        )}
      </main>
    </div>
  )
}
