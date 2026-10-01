import React, { useEffect } from 'react'
import { Clock } from 'lucide-react'

interface MockTestTimerProps {
  remainingSeconds: number
  onExpire?: () => void
}

export const MockTestTimer: React.FC<MockTestTimerProps> = ({
  remainingSeconds,
  onExpire,
}) => {
  useEffect(() => {
    if (remainingSeconds <= 0 && onExpire) {
      onExpire()
    }
  }, [remainingSeconds, onExpire])

  const formatTime = (totalSeconds: number): string => {
    const clamped = Math.max(0, totalSeconds)
    const minutes = Math.floor(clamped / 60)
    const seconds = clamped % 60
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }

  const getTimerClass = () => {
    if (remainingSeconds <= 60) return 'mt-timer-danger'
    if (remainingSeconds <= 300) return 'mt-timer-warning'
    return ''
  }

  return (
    <div
      className={`mt-timer ${getTimerClass()}`}
      data-testid="mock-test-countdown-timer"
      title="Server-synchronized examination timer"
    >
      <Clock size={16} />
      <span>{formatTime(remainingSeconds)}</span>
    </div>
  )
}
