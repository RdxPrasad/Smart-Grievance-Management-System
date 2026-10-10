import React, { useState, useEffect } from 'react'
import { api } from '../api'
import { IconAlertCircle, IconCheckCircle, IconX, IconInbox } from './Icons'
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

      setActionSuccess(`Grievance #${updateModalGrievance.id} updated to "${newStatus}".`)
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

  // Count stats from real data
  const totalCount = grievances.length
  const openCount = grievances.filter((g) => ['open', 'submitted'].includes((g.status || '').toLowerCase())).length
  const inProgressCount = grievances.filter((g) => ['under review', 'in progress'].includes((g.status || '').toLowerCase())).length
  const resolvedCount = grievances.filter((g) => (g.status || '').toLowerCase() === 'resolved').length

  return (
    <div>
      {/* Overview Metric Bar */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">
            {user.role === 'admin' ? 'Total Grievances' : 'Department Grievances'}
          </div>
          <div className="stat-value">{totalCount}</div>
        </div>

        <div className="stat-card stat-card--open">
          <div className="stat-label">Pending Review</div>
          <div className="stat-value">{openCount}</div>
        </div>

        <div className="stat-card stat-card--progress">
          <div className="stat-label">In Progress</div>
          <div className="stat-value">{inProgressCount}</div>
        </div>

        <div className="stat-card stat-card--resolved">
          <div className="stat-label">Resolved</div>
          <div className="stat-value">{resolvedCount}</div>
        </div>
      </div>

      {actionSuccess && (
        <div className="alert alert-success">
          <IconCheckCircle className="alert-icon" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <IconAlertCircle className="alert-icon" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Table Card */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap' }}>
          <div>
            <h2 className="card-title">
              {user.role === 'admin' ? 'All Grievances' : 'Department Resolution Queue'}
            </h2>
            <p className="card-desc">
              Review grievances, update statuses, and append official remarks.
            </p>
          </div>

          {/* Filter & Search Controls */}
          <div className="filter-bar">
            <input
              type="text"
              className="form-input"
              placeholder="Search complaints..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />

            <select
              className="form-select"
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
          <div className="loading-inline">
            <div className="spinner"></div>
            <span>Loading grievances...</span>
          </div>
        ) : filteredGrievances.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <IconInbox size={48} />
            </div>
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
                  <th>Student</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredGrievances.map((g) => (
                  <tr key={g.id}>
                    <td className="td-id">#{g.id}</td>
                    <td className="td-complaint">
                      <div className="td-complaint-text">
                        {g.complaint}
                      </div>
                      <div className="td-complaint-meta">
                        Category #{g.category_id} / Dept #{g.department_id}
                      </div>
                    </td>
                    <td className="text-sm text-muted">
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
                    <td className="td-actions">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleOpenUpdateModal(g)}
                      >
                        Update
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
                <p className="modal-header-desc">
                  Change resolution state and record official remarks
                </p>
              </div>
              <button className="btn-close" onClick={() => setUpdateModalGrievance(null)}>
                <IconX />
              </button>
            </div>

            <form onSubmit={handleSaveStatusUpdate}>
              <div className="modal-body">
                <div className="grievance-summary">
                  <div className="text-sm" style={{ fontWeight: 500, marginBottom: 4 }}>
                    Complaint:
                  </div>
                  <div className="grievance-summary-text">
                    {updateModalGrievance.complaint}
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="staff-newStatus">New Status</label>
                  <select
                    id="staff-newStatus"
                    className="form-select"
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                  >
                    <option value="Open">Open - Pending initial review</option>
                    <option value="In Progress">In Progress - Work ongoing</option>
                    <option value="Resolved">Resolved - Action completed</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="staff-statusNotes">Official Note / Remarks</label>
                  <textarea
                    id="staff-statusNotes"
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
                  {updating ? 'Saving...' : 'Confirm Update'}
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
