import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function GrievanceTimelineModal({ grievance, onClose }) {
  const [updates, setUpdates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!grievance?.id) return
    loadUpdates()
  }, [grievance?.id])

  const loadUpdates = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getGrievanceUpdates(grievance.id)
      setUpdates(data)
    } catch (err) {
      setError(err.message || 'Failed to load update history.')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const s = (status || '').toLowerCase().replace(/\s+/g, '-')
    return (
      <span className={`badge badge-${s}`}>
        <span className="badge-dot"></span>
        {status}
      </span>
    )
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Grievance #{grievance.id} Audit History</h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Official lifecycle and status change log
            </p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* Grievance Summary Box */}
          <div style={{ background: 'var(--bg-subtle)', padding: '14px', borderRadius: '8px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span className={`priority-pill priority-${(grievance.priority || '').toLowerCase()}`}>
                {grievance.priority} Priority
              </span>
              {getStatusBadge(grievance.status)}
            </div>
            <p style={{ fontSize: '14px', color: 'var(--text-main)', marginTop: '6px' }}>
              {grievance.complaint}
            </p>
          </div>

          <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px' }}>
            Resolution Timeline & Updates
          </h4>

          {loading ? (
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Loading audit trail...</p>
          ) : error ? (
            <div className="alert alert-error">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          ) : updates.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px' }}>
              <div className="empty-state-icon">📋</div>
              <h4>No updates recorded yet</h4>
              <p>This grievance is queued for department review.</p>
            </div>
          ) : (
            <div className="timeline">
              {updates.map((up) => {
                const dateStr = up.created_at 
                  ? new Date(up.created_at).toLocaleString('en-US', {
                      dateStyle: 'medium',
                      timeStyle: 'short',
                    })
                  : 'Recent'

                return (
                  <div key={up.id} className="timeline-item">
                    <div className="timeline-dot" />
                    <div className="timeline-meta">
                      <span>{dateStr}</span>
                      <span>•</span>
                      <span>Updated by User #{up.updated_by}</span>
                    </div>
                    <div className="timeline-title">
                      Status transitioned to: {getStatusBadge(up.status)}
                    </div>
                    {up.notes && (
                      <div className="timeline-note">
                        <strong>Remarks:</strong> {up.notes}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
