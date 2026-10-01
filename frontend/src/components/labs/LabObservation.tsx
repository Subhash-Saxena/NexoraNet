import React from 'react'
import { Eye } from 'lucide-react'

interface LabObservationProps {
  observation?: string | null
}

export const LabObservation: React.FC<LabObservationProps> = ({ observation }) => {
  if (!observation) return null

  return (
    <div className="lab-observation-box">
      <div className="lab-observation-header">
        <Eye size={16} />
        <span>What to Observe in Your Output</span>
      </div>
      <div className="lab-observation-text">
        {observation}
      </div>
    </div>
  )
}
