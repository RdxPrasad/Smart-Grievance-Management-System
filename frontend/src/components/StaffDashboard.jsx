import React, { useState, useEffect } from 'react'
import { api } from '../api'
import GrievanceTimelineModal from './GrievanceTimelineModal'

export default function StaffDashboard({ user }) {
  const [grievances, setGrievances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [searchTerm, setSearchTerm] = useState('')

  // Modal states
  const [timelineGrievance, setTimelineGrievance] = useState(null)
  const [updateModalGrievance, setUpdateModalGrievance] = useState(null)
  const [newStatus, setNewStatus] = useState('Open')
  const [statusNotes, setStatusNotes] = useState('')
  const [updating, setUpdating] = useState(false)
  const [actionSuccess, setActionSuccess] = useState(null)

  useEffect(() => {
    loadGrievances()
  }, [])

  const loadGrievances = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getGrievances()
      setGrievances(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch grievances.')
    } finally {
      setLoading(false)
    }
  }

  const handleOpenUpdateModal = (g) => {
    setUpdateModalGrievance(g)
    setNewStatus(g.status || 'Under Review')
    setStatusNotes('')
    setActionSuccess(null)
  }

  const handleSaveStatusUpdate = async (e) => {
    e.preventDefault()
    if (!updateModalGrievance) return

    setUpdating(true)
    setError(null)
    try {
      // 1. Update the grievance record
      await api.updateGrievance(updateModalGrievance.id, {
        complaint: updateModalGrievance.complaint,
        priority: updateModalGrievance.priority,
        status: newStatus,
        category_id: updateModalGrievance.category_id,
        department_id: updateModalGrievance.department_id,
      })

      // 2. Add remarks note if provided
      if (statusNotes.trim()) {
        await api.addGrievanceUpdate({
          grievance_id: updateModalGrievance.id,
          status: newStatus,
          notes: statusNotes.trim(),
        }).catch(() => {
          // If auto-audit already handled the transition, notes can be supplementary
        })
      }

      setActionSuccess(`Grievance #${updateModalGrievance.id} updated to ${newStatus}!`)
      setUpdateModalGrievance(null)
      await loadGrievances()
    } catch (err) {
      setError(err.message || 'Failed to update status.')
    } finally {
      setUpdating(false)
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

  // Filter logic
  const filteredGrievances = grievances.filter((g) => {
    const matchesStatus = statusFilter === 'ALL' || (g.status || '').toLowerCase() === statusFilter.toLowerCase()
    const matchesSearch = !searchTerm || (g.complaint || '').toLowerCase().includes(searchTerm.toLowerCase())
    return matchesStatus && matchesSearch
  })

  // Count stats
  const totalCount = grievances.length
  const submittedCount = grievances.filter((g) => (g.status || '').toLowerCase() === 'submitted').length
  const inProgressCount = grievances.filter((g) => ['under review', 'in progress'].includes((g.status || '').toLowerCase())).length
  const resolvedCount = grievances.filter((g) => (g.status || '').toLowerCase() === 'resolved').length

  return (
    <div>
      {/* Overview Metric Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div className="card" style={{ marginBottom: 0, padding: '16px 20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            {user.role === 'admin' ? 'Total Institutional Grievances' : 'Department Grievances'}
          </div>
          <div style={{ fontSize: '26px', fontWeight: 700, marginTop: '4px' }}>{totalCount}</div>
        </div>

        <div className="card" style={{ marginBottom: 0, padding: '16px 20px' }}>
          <div style={{ fontSize: '12px', color: 'var(--status-submitted-text)', textTransform: 'uppercase', fontWeight: 600 }}>
            Pending Review
          </div>
          <div style={{ fontSize: '26px', fontWeight: 700, marginTop: '4px', color: 'var(--status-submitted-text)' }}>
            {submittedCount}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0, padding: '16px 20px' }}>
          <div style={{ fontSize: '12px', color: '#b45309', textTransform: 'uppercase', fontWeight: 600 }}>
            In Progress / Review
          </div>
          <div style={{ fontSize: '26px', fontWeight: 700, marginTop: '4px', color: '#b45309' }}>
            {inProgressCount}
          </div>
        </div>

        <div className="card" style={{ marginBottom: 0, padding: '16px 20px' }}>
          <div style={{ fontSize: '12px', color: '#15803d', textTransform: 'uppercase', fontWeight: 600 }}>
            Resolved
          </div>
          <div style={{ fontSize: '26px', fontWeight: 700, marginTop: '4px', color: '#15803d' }}>
            {resolvedCount}
          </div>
        </div>
      </div>

      {actionSuccess && (
        <div className="alert alert-success">
          <span>✅</span>
          <span>{actionSuccess}</span>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Main Table Card */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 className="card-title">
              {user.role === 'admin' ? 'All Grievances Administration' : 'Department Resolution Queue'}
            </h2>
            <p className="card-desc">
              Review grievances, update resolution statuses, and append official audit remarks.
            </p>
          </div>

          {/* Filter & Search Controls */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <input
              type="text"
              className="form-input"
              style={{ width: '200px', padding: '6px 10px', fontSize: '13px' }}
              placeholder="Search complaints..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            <select
              className="form-select"
              style={{ width: '150px', padding: '6px 10px', fontSize: '13px' }}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>
        </div>

        {loading ? (
          <p style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
            Loading grievances...
          </p>
        ) : filteredGrievances.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">✅</div>
            <h4>No grievances matching filters</h4>
            <p>Try resetting filters or search terms.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Complaint</th>
                  <th>Student ID</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredGrievances.map((g) => (
                  <tr key={g.id}>
                    <td style={{ fontWeight: '600', color: 'var(--text-muted)' }}>
                      #{g.id}
                    </td>
                    <td style={{ maxWidth: '340px' }}>
                      <div style={{ fontWeight: '500', color: 'var(--text-main)', marginBottom: '3px' }}>
                        {g.complaint}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-subtle)' }}>
                        Category #{g.category_id} • Dept #{g.department_id}
                      </div>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                      User #{g.user_id}
                    </td>
                    <td>
                      <span className={`priority-pill priority-${(g.priority || '').toLowerCase()}`}>
                        {g.priority}
                      </span>
                    </td>
                    <td>
                      {getStatusBadge(g.status)}
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <button
                        className="btn btn-primary btn-sm"
                        style={{ marginRight: '6px' }}
                        onClick={() => handleOpenUpdateModal(g)}
                      >
                        Update Status
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => setTimelineGrievance(g)}
                        title="View audit trail"
                      >
                        History
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Status Update Action Modal */}
      {updateModalGrievance && (
        <div className="modal-overlay" onClick={() => setUpdateModalGrievance(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>Update Grievance #{updateModalGrievance.id}</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Change resolution state and record official remarks
                </p>
              </div>
              <button className="btn btn-outline btn-sm" onClick={() => setUpdateModalGrievance(null)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveStatusUpdate}>
              <div className="modal-body">
                <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: '8px', marginBottom: '16px' }}>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
                    Complaint:
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    {updateModalGrievance.complaint}
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="newStatus">New Resolution Status</label>
                  <select
                    id="newStatus"
                    className="form-select"
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                  >
                    <option value="Open">Open (Pending Initial Review)</option>
                    <option value="In Progress">In Progress (Work ongoing)</option>
                    <option value="Resolved">Resolved (Action completed)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="statusNotes">Official Note / Remarks</label>
                  <textarea
                    id="statusNotes"
                    className="form-textarea"
                    placeholder="Explain the update, next action, or resolution justification..."
                    value={statusNotes}
                    onChange={(e) => setStatusNotes(e.target.value)}
                    rows={3}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setUpdateModalGrievance(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={updating}
                >
                  {updating ? 'Saving...' : 'Confirm Status Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* History Timeline Modal */}
      {timelineGrievance && (
        <GrievanceTimelineModal
          grievance={timelineGrievance}
          onClose={() => setTimelineGrievance(null)}
        />
      )}
    </div>
  )
}
