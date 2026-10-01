import React from 'react'
import { Link } from 'react-router-dom'
import { Clock, Layers, Award, Terminal, Cpu, CheckCircle2, PlayCircle, RotateCcw } from 'lucide-react'
import type { LabBrief } from '../../types'

interface LabCardProps {
  lab: LabBrief
  onStart?: (lab: LabBrief) => void
}

export const LabCard: React.FC<LabCardProps> = ({ lab }) => {
  const getDifficultyClass = (diff: string) => {
    switch (diff.toUpperCase()) {
      case 'BEGINNER':
        return 'lab-badge-beginner'
      case 'INTERMEDIATE':
        return 'lab-badge-intermediate'
      case 'ADVANCED':
        return 'lab-badge-advanced'
      default:
        return 'lab-badge-env'
    }
  }

  const getEnvIcon = (env: string) => {
    switch (env.toUpperCase()) {
      case 'LOCAL_SYSTEM':
        return <Terminal size={12} />
      case 'CONCEPTUAL':
        return <Cpu size={12} />
      default:
        return <Terminal size={12} />
    }
  }

  const formatEnvName = (env: string) => {
    switch (env.toUpperCase()) {
      case 'LOCAL_SYSTEM':
        return 'Local Terminal'
      case 'CONCEPTUAL':
        return 'Interactive Theory'
      case 'CONTAINER':
        return 'Container (Planned)'
      case 'PCAP':
        return 'PCAP Analysis'
      default:
        return env
    }
  }

  const isCompleted = lab.user_status === 'COMPLETED'
  const isInProgress = lab.user_status === 'IN_PROGRESS'

  return (
    <div className="lab-card">
      <div className="lab-card-top">
        <div className="lab-card-badges">
          <span className={`lab-badge ${getDifficultyClass(lab.difficulty)}`}>
            {lab.difficulty}
          </span>
          <span className="lab-badge lab-badge-env">
            {getEnvIcon(lab.environment_type)}
            {formatEnvName(lab.environment_type)}
          </span>
          {isCompleted && (
            <span className="lab-badge lab-badge-status-completed">
              <CheckCircle2 size={12} /> Completed
            </span>
          )}
          {isInProgress && (
            <span className="lab-badge lab-badge-status-in-progress">
              <PlayCircle size={12} /> In Progress
            </span>
          )}
        </div>

        <h3 className="lab-card-title">{lab.title}</h3>
        <div className="lab-card-topic">
          <span>Topic:</span>
          <strong>{lab.topic_title}</strong>
        </div>

        <p className="lab-card-desc">
          {lab.description || 'Hands-on networking laboratory drill with practical validation.'}
        </p>
      </div>

      <div className="lab-card-bottom">
        <div className="lab-card-meta">
          <div className="lab-meta-item">
            <Clock size={14} />
            <span>{lab.estimated_minutes} mins</span>
          </div>
          <div className="lab-meta-item">
            <Layers size={14} />
            <span>{lab.total_steps} {lab.total_steps === 1 ? 'step' : 'steps'}</span>
          </div>
          <div className="lab-meta-item">
            <Award size={14} />
            <span>{lab.total_points} pts</span>
          </div>
        </div>

        <div className="lab-card-footer">
          {lab.latest_score_percentage !== undefined && lab.latest_score_percentage !== null ? (
            <div className="lab-card-score">
              Score: {Math.round(lab.latest_score_percentage)}%
            </div>
          ) : (
            <div />
          )}

          <Link
            to={`/labs/${lab.slug}`}
            className={`btn-lab-action ${isCompleted ? 'btn-lab-secondary' : 'btn-lab-primary'}`}
          >
            {isCompleted ? (
              <>
                <RotateCcw size={14} /> Retake / Review
              </>
            ) : isInProgress ? (
              <>
                <PlayCircle size={14} /> Resume Lab
              </>
            ) : (
              <>
                <PlayCircle size={14} /> Start Lab
              </>
            )}
          </Link>
        </div>
      </div>
    </div>
  )
}
