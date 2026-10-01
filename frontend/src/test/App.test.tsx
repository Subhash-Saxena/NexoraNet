import '@testing-library/jest-dom'
import { render, screen, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import App from '../App'

beforeEach(() => {
  const mockFetch = vi.fn().mockImplementation((url: string) => {
    if (url.includes('/api/health')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ status: 'ok', service: 'NexoraNet API' }),
      })
    }
    return Promise.resolve({
      ok: true,
      json: async () => ({ status: 'planned', module: 'test', capabilities: [] }),
    })
  })
  vi.stubGlobal('fetch', mockFetch)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('NexoraNet Application Shell', () => {
  it('renders the brand title and navigation links', async () => {
    await act(async () => {
      render(<App />)
    })

    // Verify brand identity
    expect(screen.getByText('NexoraNet')).toBeInTheDocument()

    // Verify navigation links in sidebar
    expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /networking track/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /hands-on labs/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /mock tests/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /network simulator/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /packet analysis/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /mini soc/i })).toBeInTheDocument()
  })

  it('renders the 5-stage progression path', async () => {
    await act(async () => {
      render(<App />)
    })

    expect(screen.getByText('Beginner')).toBeInTheDocument()
    expect(screen.getByText('Intermediate')).toBeInTheDocument()
    expect(screen.getByText('Advanced')).toBeInTheDocument()
    expect(screen.getByText('Cyber Defense')).toBeInTheDocument()
    expect(screen.getAllByText('Mini SOC').length).toBeGreaterThanOrEqual(1)
  })

  it('renders initial dashboard metric cards', async () => {
    await act(async () => {
      render(<App />)
    })

    expect(screen.getByText('Learning Progress')).toBeInTheDocument()
    expect(screen.getByText('Labs Completed')).toBeInTheDocument()
    expect(screen.getAllByText('Mock Tests').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Networking Skills')).toBeInTheDocument()
    expect(screen.getByText('Security Skills')).toBeInTheDocument()
    expect(screen.getByText('Current Level')).toBeInTheDocument()
  })

  it('updates backend connectivity status badge', async () => {
    await act(async () => {
      render(<App />)
    })

    expect(await screen.findByText(/Connected/i)).toBeInTheDocument()
  })
})
