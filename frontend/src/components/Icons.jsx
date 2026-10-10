import React from 'react'

/**
 * Minimal SVG icons used across the app.
 * No emoji. No icon libraries. Just clean inline SVGs.
 * All icons default to 16x16 with currentColor.
 */

export function IconX({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" {...props}>
      <path d="M4 4l8 8M12 4l-8 8" />
    </svg>
  )
}

export function IconAlertCircle({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" {...props}>
      <circle cx="8" cy="8" r="6.25" />
      <path d="M8 5v3.5M8 10.5v.5" />
    </svg>
  )
}

export function IconCheckCircle({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <circle cx="8" cy="8" r="6.25" />
      <path d="M5.5 8l2 2 3.5-3.5" />
    </svg>
  )
}

export function IconArrowRight({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M3.5 8h9M9 4.5L12.5 8 9 11.5" />
    </svg>
  )
}

export function IconInbox({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M2.5 9.5h3.25a1 1 0 011 1v.25a1.25 1.25 0 002.5 0V10.5a1 1 0 011-1h3.25" />
      <rect x="2.5" y="3" width="11" height="10" rx="1.5" />
    </svg>
  )
}

export function IconClipboard({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <rect x="3.5" y="2.5" width="9" height="11" rx="1.5" />
      <path d="M6 2.5V2a1 1 0 011-1h2a1 1 0 011 1v.5" />
      <path d="M6 6.5h4M6 9h2.5" />
    </svg>
  )
}

export function IconFilter({ size = 16, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" {...props}>
      <path d="M2 4h12M4 8h8M6 12h4" />
    </svg>
  )
}
