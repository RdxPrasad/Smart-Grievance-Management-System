import React, { useState, useEffect } from 'react'
import { api } from '../api'
import { IconAlertCircle, IconCheckCircle, IconInbox, IconArrowRight } from './Icons'
import GrievanceTimelineModal from './GrievanceTimelineModal'

export default function StudentDashboard({ user }) {
  const [grievances, setGrievances] = useState([])
  const [categories, setCategories] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)

  // Selected grievance for audit timeline modal
  const [activeGrievance, setActiveGrievance] = useState(null)

  // Form fields
  const [complaint, setComplaint] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [priority, setPriority] = useState('Medium')

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [grievanceData, catData, deptData] = await Promise.all([
        api.getGrievances(),
        api.getCategories().catch(() => []),
        api.getDepartments().catch(() => []),
      ])
      setGrievances(grievanceData)
      setCategories(catData)
      setDepartments(deptData)

      // Set defaults for selects
      if (catData.length > 0) setCategoryId(catData[0].id)
      if (deptData.length > 0) setDepartmentId(deptData[0].id)
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitGrievance = async (e) => {
    e.preventDefault()
    if (!complaint.trim()) {
      setError('Please provide a complaint description.')
      return
    }

    setSubmitting(true)
    setError(null)
    setSuccessMsg(null)

    try {
      const payload = {
        complaint: complaint.trim(),
        priority,
        status: 'Open',
        category_id: parseInt(categoryId),
        department_id: parseInt(departmentId),
      }

      await api.createGrievance(payload)
      setSuccessMsg('Grievance registered and routed to the department.')
      setComplaint('')

      // Refresh list
      const freshGrievances = await api.getGrievances()
      setGrievances(freshGrievances)
    } catch (err) {
      setError(err.message || 'Failed to submit grievance.')
    } finally {
      setSubmitting(false)
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
    <div>
      {/* 1. Grievance Submission Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Lodge a New Grievance</h2>
            <p className="card-desc">
              Your grievance will be directly routed to the responsible department.
            </p>
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <IconAlertCircle className="alert-icon" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="alert alert-success">
            <IconCheckCircle className="alert-icon" />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmitGrievance}>
          <div className="form-group">
            <label className="form-label" htmlFor="student-complaint">Complaint Description</label>
            <textarea
              id="student-complaint"
              className="form-textarea"
              placeholder="Clearly describe the issue, location, and any relevant details..."
              value={complaint}
              onChange={(e) => setComplaint(e.target.value)}
              rows={3}
              required
            />
          </div>

          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="student-category">Category</label>
              <select
                id="student-category"
                className="form-select"
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="student-department">Department</label>
              <select
                id="student-department"
                className="form-select"
                value={departmentId}
                onChange={(e) => setDepartmentId(e.target.value)}
              >
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label" htmlFor="student-priority">Priority</label>
              <select
                id="student-priority"
                className="form-select"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              >
                <option value="Low">Low - General inquiry, minor issue</option>
                <option value="Medium">Medium - Standard resolution expected</option>
                <option value="High">High - Affecting coursework or schedule</option>
              </select>
            </div>

            <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
              <button
                type="submit"
                className="btn btn-primary btn-lg"
                style={{ width: '100%' }}
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Submit Grievance'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* 2. My Grievances History Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">My Registered Grievances</h2>
            <p className="card-desc">
              Track progress and view staff resolution updates.
            </p>
          </div>
          <span className="text-sm text-muted">
            Total: <strong>{grievances.length}</strong>
          </span>
        </div>

        {loading ? (
          <div className="loading-inline">
            <div className="spinner"></div>
            <span>Loading your grievances...</span>
          </div>
        ) : grievances.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <IconInbox size={48} />
            </div>
            <h4>No grievances submitted yet</h4>
            <p>Use the form above to register your first grievance.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Complaint</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {grievances.map((g) => (
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
                        className="btn btn-secondary btn-sm"
                        onClick={() => setActiveGrievance(g)}
                        title="View status updates timeline"
                      >
                        Track Progress
                        <IconArrowRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Timeline Modal */}
      {activeGrievance && (
        <GrievanceTimelineModal
          grievance={activeGrievance}
          onClose={() => setActiveGrievance(null)}
        />
      )}
    </div>
  )
}
