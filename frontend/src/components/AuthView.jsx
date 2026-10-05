import React, { useState } from 'react'
import { supabase } from '../supabaseClient'

export default function AuthView({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccessMsg(null)
    setLoading(true)

    try {
      if (isLogin) {
        // Log in existing user
        const { data, error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        })
        if (signInError) throw signInError
        if (onAuthSuccess) onAuthSuccess(data.session)
      } else {
        // Sign up new user
        const { data, error: signUpError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: {
              name: fullName.trim() || email.split('@')[0],
            },
          },
        })
        if (signUpError) throw signUpError

        // Supabase sends a confirmation email unless email confirmations are disabled
        if (data.session) {
          if (onAuthSuccess) onAuthSuccess(data.session)
        } else {
          setSuccessMsg('Account created successfully! Please check your email for confirmation or sign in.')
          setIsLogin(true)
        }
      }
    } catch (err) {
      setError(err.message || 'An error occurred during authentication.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '440px', margin: '40px auto 0' }}>
      <div className="card">
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div className="brand-icon" style={{ margin: '0 auto 14px', width: '48px', height: '48px', fontSize: '22px' }}>
            SG
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '6px' }}>
            {isLogin ? 'Welcome Back' : 'Create an Account'}
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            {isLogin 
              ? 'Sign in to submit grievances and track resolution updates' 
              : 'Register as a student to log and track your complaints'}
          </p>
        </div>

        {/* Tab switch */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', background: 'var(--bg-subtle)', padding: '4px', borderRadius: '8px' }}>
          <button
            type="button"
            className={`btn ${isLogin ? 'btn-primary' : 'btn-outline'}`}
            style={{ flex: 1, padding: '8px', border: 'none' }}
            onClick={() => { setIsLogin(true); setError(null); }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`btn ${!isLogin ? 'btn-primary' : 'btn-outline'}`}
            style={{ flex: 1, padding: '8px', border: 'none' }}
            onClick={() => { setIsLogin(false); setError(null); }}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="alert alert-success">
            <span>✅</span>
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label className="form-label" htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                type="text"
                className="form-input"
                placeholder="e.g. Rahul Sharma"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required={!isLogin}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label" htmlFor="email">Institute Email</label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="user@institute.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '11px', marginTop: '8px' }}
            disabled={loading}
          >
            {loading ? 'Please wait...' : isLogin ? 'Sign In to Portal' : 'Create Student Account'}
          </button>
        </form>
      </div>
    </div>
  )
}
