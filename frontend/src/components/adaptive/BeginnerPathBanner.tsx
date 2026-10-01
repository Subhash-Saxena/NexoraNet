import React from 'react'
import { Link } from 'react-router-dom'
import { Rocket, ArrowRight, BookOpen } from 'lucide-react'

export const BeginnerPathBanner: React.FC = () => {
  const steps = [
    { num: '01', title: 'Networking Fundamentals', path: '/learning/topics/networking-fundamentals' },
    { num: '02', title: 'OSI Reference Model', path: '/learning/topics/osi-model' },
    { num: '03', title: 'TCP/IP Protocol Suite', path: '/learning/topics/tcp-ip-model' },
    { num: '04', title: 'IPv4 Addressing', path: '/learning/topics/ipv4-addressing' },
    { num: '05', title: 'TCP & UDP Mechanics', path: '/learning/topics/tcp-udp' },
  ]

  return (
    <div className="ad-onboarding-banner" data-testid="beginner-path-banner">
      <div className="ad-onboard-title">
        <Rocket size={22} color="#38bdf8" />
        Recommended Foundational Sequence
      </div>
      <div className="ad-onboard-desc">
        Personalized adaptive recommendations unlock after completing 1–2 tests or lessons.
        For new students and cybersecurity cadets, we recommend working through these core networking modules in sequence:
      </div>

      <div className="ad-path-steps">
        {steps.map((s) => (
          <Link
            key={s.num}
            to={s.path}
            className="ad-path-step-card"
            style={{ textDecoration: 'none' }}
          >
            <div className="ad-step-number">Step {s.num}</div>
            <div className="ad-step-name">{s.title}</div>
          </Link>
        ))}
      </div>

      <div>
        <Link to="/learning" className="ad-btn-primary" data-testid="start-learning-path-btn">
          <BookOpen size={16} />
          Start Networking Track
          <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  )
}
