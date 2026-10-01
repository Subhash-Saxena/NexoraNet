import { useEffect, useState, useCallback } from 'react'
import { apiService } from '../services/api'
import type { BackendHealthState, HealthResponse } from '../types'

interface UseHealthCheckResult {
  status: BackendHealthState
  data: HealthResponse | null
  error: string | null
  lastChecked: Date | null
  checkNow: () => Promise<void>
}

export function useHealthCheck(pollIntervalMs: number = 15000): UseHealthCheckResult {
  const [status, setStatus] = useState<BackendHealthState>('checking')
  const [data, setData] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const checkNow = useCallback(async () => {
    try {
      const response = await apiService.checkHealth()
      if (response.status === 'ok') {
        setStatus('connected')
        setData(response)
        setError(null)
      } else {
        setStatus('disconnected')
        setError('Unexpected status payload')
      }
      setLastChecked(new Date())
    } catch (err: unknown) {
      setStatus('disconnected')
      setError(err instanceof Error ? err.message : 'Backend unreachable')
      setLastChecked(new Date())
    }
  }, [])

  useEffect(() => {
    let isSubscribed = true

    const runHealthCheck = async () => {
      try {
        const response = await apiService.checkHealth()
        if (!isSubscribed) return

        if (response.status === 'ok') {
          setStatus('connected')
          setData(response)
          setError(null)
        } else {
          setStatus('disconnected')
          setError('Unexpected status payload')
        }
        setLastChecked(new Date())
      } catch (err: unknown) {
        if (!isSubscribed) return
        setStatus('disconnected')
        setError(err instanceof Error ? err.message : 'Backend unreachable')
        setLastChecked(new Date())
      }
    }

    void runHealthCheck()

    const interval = setInterval(() => {
      void runHealthCheck()
    }, pollIntervalMs)

    return () => {
      isSubscribed = false
      clearInterval(interval)
    }
  }, [pollIntervalMs])

  return { status, data, error, lastChecked, checkNow }
}
