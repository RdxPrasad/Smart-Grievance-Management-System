import React, { useEffect, useState } from 'react'
import { api } from '../api'
import { IconAlertCircle, IconX, IconClipboard } from './Icons'

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
            <h3>Grievance #{grievance.id} - Audit History</h3>
            <p className="modal-header-desc">
              Lifecycle and status change log
            </p>
          </div>
          <button className="btn-close" onClick={onClose}>
            <IconX />
          </button>
        </div>

        <div className="modal-body">
          {/* Grievance Summary Box */}
          <div className="grievance-summary">
            <div className="grievance-summary-row">
              <span className={`priority-pill priority-${(grievance.priority || '').toLowerCase()}`}>
                {grievance.priority} Priority
              </span>
              {getStatusBadge(grievance.status)}
            </div>
            <p className="grievance-summary-text">
              {grievance.complaint}
            </p>
          </div>

          <h4 className="section-heading">
            Resolution Timeline
          </h4>

          {loading ? (
            <div className="loading-inline">
              <div className="spinner"></div>
              <span>Loading audit trail...</span>
            </div>
          ) : error ? (
            <div className="alert alert-error">
              <IconAlertCircle className="alert-icon" />
              <span>{error}</span>
            </div>
          ) : updates.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px' }}>
              <div className="empty-state-icon">
                <IconClipboard size={48} />
              </div>
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
                      <span className="timeline-meta-sep">/</span>
                      <span>Updated by User #{up.updated_by}</span>
                    </div>
                    <div className="timeline-title">
                      Status changed to: {getStatusBadge(up.status)}
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
