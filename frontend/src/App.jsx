import React, { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import { api } from './api'
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
      <div className="app-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="brand-icon" style={{ margin: '0 auto 16px', width: '48px', height: '48px', fontSize: '20px' }}>
            SG
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', fontWeight: '500' }}>
            Initializing Smart Grievance Portal...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="app-container">
      <Navbar user={currentUser} onSignOut={handleSignOut} />

      <main className="main-content">
        {/* If backend is unreachable, show clear alert */}
        {error && (
          <div className="alert alert-error" style={{ marginBottom: '24px' }}>
            <span>⚠️</span>
            <div style={{ flex: 1 }}>
              <strong>Backend Connection Notice:</strong> {error}
              <div style={{ fontSize: '12px', marginTop: '4px' }}>
                Make sure to start the backend with: <code>uvicorn app.main:app --reload</code>
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
              <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Admin View Mode:</span>
                <div style={{ display: 'inline-flex', background: 'var(--bg-subtle)', padding: '3px', borderRadius: '6px' }}>
                  <button
                    className={`btn btn-sm ${adminViewMode === 'admin' ? 'btn-primary' : 'btn-outline'}`}
                    style={{ border: 'none' }}
                    onClick={() => setAdminViewMode('admin')}
                  >
                    Admin / Staff Queue
                  </button>
                  <button
                    className={`btn btn-sm ${adminViewMode === 'student' ? 'btn-primary' : 'btn-outline'}`}
                    style={{ border: 'none' }}
                    onClick={() => setAdminViewMode('student')}
                  >
                    Student Lodging View
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
