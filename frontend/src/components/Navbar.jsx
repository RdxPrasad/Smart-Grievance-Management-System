import React from 'react'
import { supabase } from '../supabaseClient'

export default function Navbar({ user, onSignOut }) {
  const handleSignOut = async () => {
    await supabase.auth.signOut()
    if (onSignOut) onSignOut()
  }

  const roleClass = user?.role === 'admin' 
    ? 'role-admin' 
    : user?.role === 'staff' 
      ? 'role-staff' 
      : 'role-student'

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand">
          <div className="brand-icon">SG</div>
          <div className="brand-text">
            <h1>Smart Grievance Portal</h1>
            <p>Institutional Resolution System</p>
          </div>
        </div>

        {user && (
          <div className="nav-user">
            <div className="user-badge">
              <span className="user-name">{user.name || user.email}</span>
              <span className={`role-pill ${roleClass}`}>
                {user.role}
              </span>
            </div>

            <button 
              className="btn btn-secondary btn-sm" 
              onClick={handleSignOut}
              title="Sign out of your account"
            >
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
