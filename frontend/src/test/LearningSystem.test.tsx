import '@testing-library/jest-dom'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { LearningRoadmap } from '../components/learning/LearningRoadmap'
import { OSIStackDiagram } from '../components/learning/diagrams/OSIStackDiagram'
import { TCPHandshakeDiagram } from '../components/learning/diagrams/TCPHandshakeDiagram'
import { DNSResolutionDiagram } from '../components/learning/diagrams/DNSResolutionDiagram'
import { DHCPSequenceDiagram } from '../components/learning/diagrams/DHCPSequenceDiagram'
import { EncapsulationDiagram } from '../components/learning/diagrams/EncapsulationDiagram'
import { CalloutCard } from '../components/learning/CalloutCard'
import { MarkdownContent } from '../components/learning/MarkdownContent'
import { LearningPage } from '../pages/Learning/LearningPage'
import { TopicPage } from '../pages/Learning/TopicPage'
import { LessonPage } from '../pages/Learning/LessonPage'
import { BookmarksPage } from '../pages/Learning/BookmarksPage'

beforeEach(() => {
  const mockFetch = vi.fn().mockImplementation((url: string) => {
    if (url.includes('/api/health')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ status: 'ok', service: 'NexoraNet API' }),
      })
    }
    if (url.includes('/api/v1/learning/progress')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          overall_percentage: 42,
          total_lessons: 38,
          completed_lessons: 16,
          in_progress_lessons: 4,
          remaining_lessons: 18,
          current_level: 'INTERMEDIATE',
          beginner_progress: { level: 'BEGINNER', total_lessons: 16, completed_lessons: 16, percentage: 100 },
          intermediate_progress: { level: 'INTERMEDIATE', total_lessons: 14, completed_lessons: 0, percentage: 0 },
          advanced_progress: { level: 'ADVANCED', total_lessons: 8, completed_lessons: 0, percentage: 0 },
          continue_learning: {
            lesson_id: 17,
            lesson_title: 'Subnetting Primer: Powers of 2 & Binary Foundations',
            lesson_slug: 'subnetting-primer-powers-of-2-binary-foundations',
            topic_title: 'Subnetting & CIDR Calculation',
            topic_slug: 'subnetting-cidr-calculation',
            module_title: 'Subnetting & IP Addressing Architecture',
            module_slug: 'subnetting-ip-addressing-architecture',
            difficulty: 'INTERMEDIATE',
            estimated_minutes: 25,
            lesson_index: 1,
            total_topic_lessons: 4,
          },
        }),
      })
    }
    if (url.includes('/api/v1/courses/')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          id: 1,
          title: 'Networking & Cybersecurity Engineering',
          slug: 'networking-cybersecurity',
          description: 'Comprehensive curriculum from bitstreams to threat defense.',
          level: 'BEGINNER',
          estimated_hours: 120,
          modules_count: 19,
          modules: [
            {
              id: 1,
              course_id: 1,
              title: 'Networking Fundamentals & Architectures',
              slug: 'networking-fundamentals-architectures',
              order_index: 1,
              difficulty: 'BEGINNER',
              topics: [
                {
                  id: 1,
                  module_id: 1,
                  title: 'Network Topologies & Types',
                  slug: 'network-topologies-types',
                  difficulty: 'BEGINNER',
                  order_index: 1,
                },
              ],
            },
          ],
        }),
      })
    }
    if (url.includes('/api/v1/topics/')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          id: 1,
          module_id: 1,
          module_title: 'Networking Fundamentals & Architectures',
          module_slug: 'networking-fundamentals-architectures',
          course_id: 1,
          course_title: 'Networking & Cybersecurity Engineering',
          course_slug: 'networking-cybersecurity',
          title: 'OSI 7-Layer Architecture Model',
          slug: 'osi-7-layer-model',
          description: 'Master the 7-layer reference model from physical bits to application protocols.',
          difficulty: 'BEGINNER',
          order_index: 1,
          estimated_minutes: 45,
          learning_objectives: ['Identify all 7 layers', 'Explain encapsulation'],
          security_relevance: 'Attackers target different layers using distinct exploits.',
          prerequisites: [],
          lessons: [
            {
              id: 1,
              topic_id: 1,
              title: 'OSI Model Deep-Dive: Physical to Transport',
              slug: 'osi-model-deep-dive-physical-to-transport',
              content_type: 'LESSON',
              order_index: 1,
              estimated_minutes: 20,
              difficulty: 'BEGINNER',
              status: 'COMPLETED',
              is_bookmarked: true,
            },
          ],
          lessons_count: 1,
          completed_lessons_count: 1,
          completion_percentage: 100,
          related_labs: [{ id: 1, title: 'Wireshark Layer Dissection', slug: 'wireshark-layer-dissection', difficulty: 'BEGINNER', status: 'DRAFT' }],
          related_mock_tests: [{ id: 1, title: 'OSI Model Qualifier', slug: 'osi-model-qualifier', difficulty: 'BEGINNER', status: 'DRAFT' }],
          next_topic: null,
          previous_topic: null,
        }),
      })
    }
    if (url.includes('/api/v1/lessons/')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          id: 1,
          topic_id: 1,
          topic_title: 'OSI 7-Layer Architecture Model',
          topic_slug: 'osi-7-layer-model',
          module_id: 1,
          module_title: 'Networking Fundamentals & Architectures',
          module_slug: 'networking-fundamentals-architectures',
          course_id: 1,
          course_title: 'Networking & Cybersecurity Engineering',
          course_slug: 'networking-cybersecurity',
          title: 'OSI Model Deep-Dive: Physical to Transport',
          slug: 'osi-model-deep-dive-physical-to-transport',
          description: 'A comprehensive study of Layers 1 through 4.',
          content: '# OSI 7-Layer Model\n\nNetworking operates in distinct modular layers.\n\n> [!NOTE]\n> Layer 1 is physical bits, Layer 4 is TCP segments.\n\n[DIAGRAM:osi_stack]\n',
          content_type: 'LESSON',
          order_index: 1,
          estimated_minutes: 20,
          difficulty: 'BEGINNER',
          status: 'COMPLETED',
          is_bookmarked: false,
          next_lesson: null,
          previous_lesson: null,
        }),
      })
    }
    if (url.includes('/api/v1/learning/bookmarks')) {
      return Promise.resolve({
        ok: true,
        json: async () => [
          {
            id: 1,
            lesson_id: 1,
            lesson_title: 'OSI Model Deep-Dive: Physical to Transport',
            lesson_slug: 'osi-model-deep-dive-physical-to-transport',
            topic_title: 'OSI 7-Layer Architecture Model',
            topic_slug: 'osi-7-layer-model',
            module_title: 'Networking Fundamentals',
            module_slug: 'networking-fundamentals',
            difficulty: 'BEGINNER',
            estimated_minutes: 20,
            created_at: '2026-09-29T12:00:00Z',
          },
        ],
      })
    }
    return Promise.resolve({
      ok: true,
      json: async () => ({ status: 'ok' }),
    })
  })
  vi.stubGlobal('fetch', mockFetch)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('Step 3 — Interactive Diagrams', () => {
  it('renders OSIStackDiagram with clickable layers and threat details', () => {
    render(<OSIStackDiagram />)
    expect(screen.getByText('Interactive OSI 7-Layer Architecture Model')).toBeInTheDocument()
    expect(screen.getByText('Application Layer')).toBeInTheDocument()
    expect(screen.getByText('Physical Layer')).toBeInTheDocument()

    // Click Layer 7 Application
    fireEvent.click(screen.getByText('Application Layer'))
    expect(screen.getAllByText('Application Layer').length).toBeGreaterThanOrEqual(1)
  })

  it('renders TCPHandshakeDiagram with step state transitions', () => {
    render(<TCPHandshakeDiagram />)
    expect(screen.getByText('Interactive TCP 3-Way Handshake & State Machine')).toBeInTheDocument()

    // Step forward
    fireEvent.click(screen.getByRole('button', { name: /next step/i }))
    expect(screen.getByText(/SYN_SENT/i)).toBeInTheDocument()

    // Simulate SYN flood toggle
    fireEvent.click(screen.getByRole('button', { name: /simulate syn flood/i }))
    expect(screen.getByText(/Kernel Backlog Queue Exhaustion/i)).toBeInTheDocument()
  })

  it('renders DNSResolutionDiagram with step pipeline and attack toggle', () => {
    render(<DNSResolutionDiagram />)
    expect(screen.getByText('Recursive DNS Resolution & Zone Hierarchy')).toBeInTheDocument()
    expect(screen.getByText('Step 1 of 6')).toBeInTheDocument()

    // Toggle Kaminsky exploit
    fireEvent.click(screen.getByRole('button', { name: /dns cache poisoning/i }))
    expect(screen.getByText(/Kaminsky DNS Cache Poisoning Attack/i)).toBeInTheDocument()
  })

  it('renders DHCPSequenceDiagram with DORA letters and rogue mode', () => {
    render(<DHCPSequenceDiagram />)
    expect(screen.getByText('Interactive DHCP DORA Process (RFC 2131)')).toBeInTheDocument()
    expect(screen.getAllByText('DHCP Discover').length).toBeGreaterThanOrEqual(1)

    // Click Offer
    fireEvent.click(screen.getAllByText('DHCP Offer')[0])
    expect(screen.getAllByText('DHCP Offer').length).toBeGreaterThanOrEqual(1)

    // Toggle rogue mode
    fireEvent.click(screen.getByRole('button', { name: /rogue dhcp/i }))
    expect(screen.getByText(/Rogue DHCP Server Attack/i)).toBeInTheDocument()
  })

  it('renders EncapsulationDiagram and header inspector', () => {
    render(<EncapsulationDiagram />)
    expect(screen.getByText('Interactive Packet Encapsulation & Protocol Header Deconstruction')).toBeInTheDocument()
    expect(screen.getByText('Ethernet II Header')).toBeInTheDocument()
    expect(screen.getByText('IPv4 Header')).toBeInTheDocument()
    expect(screen.getByText('TCP Header')).toBeInTheDocument()
  })
})

describe('Step 3 — Educational Concept Components', () => {
  it('renders CalloutCard in single mode and multi-tab perspective mode', () => {
    render(
      <CalloutCard
        perspectives={[
          { type: 'bca_simple', title: 'Simple Idea', content: 'Like sending a letter.' },
          { type: 'technical', title: 'Tech Details', content: 'Uses TCP port 80.' },
          { type: 'security', title: 'Attack Angle', content: 'Cleartext sniffing.' },
        ]}
      />
    )
    expect(screen.getAllByText('Simple Idea').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Like sending a letter.')).toBeInTheDocument()

    // Switch tab
    fireEvent.click(screen.getByRole('button', { name: /Tech Details/i }))
    expect(screen.getAllByText('Tech Details').length).toBeGreaterThanOrEqual(1)
  })

  it('renders MarkdownContent parser with callouts and diagram shortcode', () => {
    const raw = '# Title Here\n\nParagraph text\n\n> [!NOTE]\n> Student note\n\n[DIAGRAM:osi_stack]\n'
    render(<MarkdownContent content={raw} />)
    expect(screen.getByText('Title Here')).toBeInTheDocument()
    expect(screen.getByText('Paragraph text')).toBeInTheDocument()
    expect(screen.getByText('Student note')).toBeInTheDocument()
    expect(screen.getByText('Interactive OSI 7-Layer Architecture Model')).toBeInTheDocument()
  })
})

describe('Step 3 — Learning Roadmap', () => {
  it('allows switching tracks from Beginner to Intermediate and Advanced', () => {
    render(
      <MemoryRouter>
        <LearningRoadmap />
      </MemoryRouter>
    )

    expect(screen.getAllByText('Networking Fundamentals').length).toBeGreaterThanOrEqual(1)

    // Click Intermediate
    fireEvent.click(screen.getByRole('button', { name: 'INTERMEDIATE' }))
    expect(screen.getAllByText('Subnetting & CIDR').length).toBeGreaterThanOrEqual(1)

    // Click Advanced
    fireEvent.click(screen.getByRole('button', { name: 'ADVANCED' }))
    expect(screen.getAllByText('Packet Analysis & PCAP').length).toBeGreaterThanOrEqual(1)
  })
})

describe('Step 3 — Pages & Routing', () => {
  it('renders LearningPage with telemetry, 3 track cards, and continue card', async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <LearningPage />
        </MemoryRouter>
      )
    })

    expect(screen.getByText('Structured Networking Curriculum')).toBeInTheDocument()
    expect(screen.getByText('Beginner Track')).toBeInTheDocument()
    expect(screen.getByText('Intermediate Track')).toBeInTheDocument()
    expect(screen.getByText('Advanced Defense')).toBeInTheDocument()
    expect(screen.getByText(/Subnetting Primer/i)).toBeInTheDocument()
  })

  it('renders TopicPage with objectives, lessons list, and security relevance', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/learning/topics/osi-7-layer-model']}>
          <Routes>
            <Route path="/learning/topics/:topicSlug" element={<TopicPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(await screen.findByRole('heading', { name: /OSI 7-Layer Architecture Model/i })).toBeInTheDocument()
    expect(screen.getByText('Learning Objectives')).toBeInTheDocument()
    expect(screen.getByText('Identify all 7 layers')).toBeInTheDocument()
    expect(screen.getByText('Cybersecurity Relevance')).toBeInTheDocument()
  })

  it('renders LessonPage with reading pane, callout, and complete action', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/learning/lessons/osi-model-deep-dive-physical-to-transport']}>
          <Routes>
            <Route path="/learning/lessons/:lessonSlug" element={<LessonPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(await screen.findByRole('heading', { name: /OSI Model Deep-Dive: Physical to Transport/i })).toBeInTheDocument()
    expect(screen.getByText('Networking operates in distinct modular layers.')).toBeInTheDocument()
    expect(screen.getAllByText('Completed').length).toBeGreaterThanOrEqual(1)
  })

  it('renders BookmarksPage with saved lesson list', async () => {
    await act(async () => {
      render(
        <MemoryRouter initialEntries={['/learning/bookmarks']}>
          <Routes>
            <Route path="/learning/bookmarks" element={<BookmarksPage />} />
          </Routes>
        </MemoryRouter>
      )
    })

    expect(await screen.findByRole('heading', { name: /Saved Learning Bookmarks/i })).toBeInTheDocument()
    expect(screen.getByText('OSI Model Deep-Dive: Physical to Transport')).toBeInTheDocument()
  })
})
