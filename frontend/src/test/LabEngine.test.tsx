import '@testing-library/jest-dom'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

// Inputs
import { SingleChoiceInput } from '../components/labs/inputs/SingleChoiceInput'
import { MultipleChoiceInput } from '../components/labs/inputs/MultipleChoiceInput'
import { TextInput } from '../components/labs/inputs/TextInput'
import { NumericInput } from '../components/labs/inputs/NumericInput'
import { IPAddressInput } from '../components/labs/inputs/IPAddressInput'
import { CIDRInput } from '../components/labs/inputs/CIDRInput'
import { PortInput } from '../components/labs/inputs/PortInput'
import { SubnetInput } from '../components/labs/inputs/SubnetInput'
import { LabAnswerInput } from '../components/labs/inputs/LabAnswerInput'

// Lab Components
import { LabCard } from '../components/labs/LabCard'
import { LabFilters } from '../components/labs/LabFilters'
import { LabStepList } from '../components/labs/LabStepList'
import { LabInstructions } from '../components/labs/LabInstructions'
import { LabObservation } from '../components/labs/LabObservation'
import { LabHint } from '../components/labs/LabHint'
import { LabFeedback } from '../components/labs/LabFeedback'
import { LabCompletion } from '../components/labs/LabCompletion'

// Pages
import { LabsPage } from '../pages/Labs/LabsPage'
import { LabDetailPage } from '../pages/Labs/LabDetailPage'
import { LabHistoryPage } from '../pages/Labs/LabHistoryPage'
import type { LabBrief, LabDetail, LabStepDetail } from '../types'

const mockLabBrief: LabBrief = {
  id: 1,
  topic_id: 2,
  topic_title: 'IP Addressing & Subnetting',
  topic_slug: 'ip-addressing-subnetting',
  title: 'Find Your Local IPv4 Address',
  slug: 'find-your-local-ipv4-address',
  description: 'Inspect your local host network interface and record your private IPv4 address.',
  difficulty: 'BEGINNER',
  estimated_minutes: 15,
  environment_type: 'LOCAL_SYSTEM',
  status: 'PUBLISHED',
  is_published: true,
  total_steps: 2,
  total_points: 20,
  user_status: 'IN_PROGRESS',
  latest_score_percentage: 50,
}

const mockStep1: LabStepDetail = {
  id: 101,
  step_number: 1,
  title: 'Execute Network Configuration Command',
  description: 'Run the network interrogation tool for your OS.',
  instructions:
    'Open your terminal and run the network configuration command corresponding to your OS:\n\n* **Windows (PowerShell or CMD)**: `ipconfig`\n* **Linux**: `ip addr`\n* **macOS**: `ifconfig`\n\nObserve the output.',
  hint: 'On Windows, run ipconfig in CMD or PowerShell.',
  expected_observation: 'A list of network adapters with IPv4 addresses.',
  validation_type: 'SINGLE_CHOICE',
  points: 10,
  is_required: true,
  safe_input_config: {
    validation_type: 'SINGLE_CHOICE',
    options: [
      { id: 'ipconfig', text: 'ipconfig' },
      { id: 'ip addr', text: 'ip addr' },
      { id: 'ifconfig', text: 'ifconfig' },
    ],
  },
  questions: [
    {
      id: 201,
      question_text: 'Which command utility did you run?',
      question_type: 'SINGLE_CHOICE',
      points: 10,
      order_index: 1,
      safe_input_config: {
        validation_type: 'SINGLE_CHOICE',
        options: [
          { id: 'ipconfig', text: 'ipconfig' },
          { id: 'ip addr', text: 'ip addr' },
        ],
      },
    },
  ],
  is_completed: true,
  points_earned: 10,
  latest_submission: {
    id: 901,
    step_id: 101,
    submitted_answer: 'ipconfig',
    is_correct: true,
    points_earned: 10,
    hint_used: false,
    feedback: 'Correct! ipconfig is the standard Windows command.',
    submitted_at: '2026-09-29T12:00:00Z',
  },
}

const mockStep2: LabStepDetail = {
  id: 102,
  step_number: 2,
  title: 'Enter Your Local IPv4 Address',
  description: 'Locate the IPv4 Address line on your active adapter.',
  instructions: 'Find the IPv4 line (e.g. 192.168.1.50) and submit it.',
  hint: 'Look for IPv4 Address or inet followed by 4 numbers.',
  expected_observation: 'A 4-octet IPv4 address like 192.168.X.X or 10.X.X.X.',
  validation_type: 'IP_ADDRESS',
  points: 10,
  is_required: true,
  safe_input_config: {
    validation_type: 'IP_ADDRESS',
    placeholder: '192.168.1.100',
  },
  questions: [
    {
      id: 202,
      question_text: 'Enter your verified local IPv4 address:',
      question_type: 'IP_ADDRESS',
      points: 10,
      order_index: 2,
      safe_input_config: {
        validation_type: 'IP_ADDRESS',
      },
    },
  ],
  is_completed: false,
  points_earned: 0,
  latest_submission: null,
}

const mockLabDetail: LabDetail = {
  ...mockLabBrief,
  instructions: 'Lab overview instructions',
  objectives: ['Identify network interface', 'Read IPv4 address'],
  prerequisites: ['Terminal basics'],
  steps: [mockStep1, mockStep2],
  active_attempt_id: 501,
  active_attempt_status: 'IN_PROGRESS',
  active_attempt_score: 10,
  active_attempt_percentage: 50,
  active_attempt_time_taken: 120,
  attempt_number: 1,
}

beforeEach(() => {
  const mockFetch = vi.fn().mockImplementation((url: string, _opts?: RequestInit) => {
    // GET /api/v1/labs/telemetry
    if (url.includes('/api/v1/labs/telemetry')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          total_labs: 18,
          completed_labs: 3,
          in_progress_labs: 2,
          average_score: 88,
          beginner_completed: 3,
          beginner_total: 10,
          intermediate_completed: 0,
          intermediate_total: 8,
          advanced_completed: 0,
          advanced_total: 0,
        }),
      })
    }

    // POST /api/v1/lab-attempts/501/steps/102/submit
    if (url.includes('/steps/102/submit')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          step_id: 102,
          attempt_id: 501,
          is_correct: true,
          points_earned: 10,
          max_points: 10,
          feedback: 'Correct! Valid local IPv4 address verified.',
          explanation: 'RFC 1918 addresses are used for non-internet-routable local traffic.',
          attempt_score: 20,
          attempt_total_points: 20,
          attempt_percentage: 100,
          is_lab_completed: true,
        }),
      })
    }

    // POST /api/v1/lab-attempts/501/retry
    if (url.includes('/retry')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          ...mockLabDetail,
          active_attempt_status: 'IN_PROGRESS',
          active_attempt_score: 0,
          active_attempt_percentage: 0,
          steps: [
            { ...mockStep1, is_completed: false, points_earned: 0, latest_submission: null },
            { ...mockStep2, is_completed: false, points_earned: 0, latest_submission: null },
          ],
        }),
      })
    }

    // POST /api/v1/labs/find-your-local-ipv4-address/start or GET
    if (url.includes('/api/v1/labs/find-your-local-ipv4-address/start') || url.includes('/api/v1/labs/find-your-local-ipv4-address')) {
      return Promise.resolve({
        ok: true,
        json: async () => mockLabDetail,
      })
    }

    // GET /api/v1/lab-attempts/501
    if (url.includes('/api/v1/lab-attempts/501')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          id: 501,
          lab_id: 1,
          lab_title: 'Find Your Local IPv4 Address',
          lab_slug: 'find-your-local-ipv4-address',
          lab_difficulty: 'BEGINNER',
          attempt_number: 1,
          status: 'COMPLETED',
          score: 20,
          total_points: 20,
          percentage: 100,
          started_at: '2026-09-29T10:00:00Z',
          completed_at: '2026-09-29T10:05:00Z',
          time_taken_seconds: 300,
          submissions: [
            {
              step_id: 101,
              step_number: 1,
              step_title: 'Execute Network Configuration Command',
              submitted_answer: 'ipconfig',
              is_correct: true,
              points_earned: 10,
              max_points: 10,
              hint_used: false,
              feedback: 'Correct! ipconfig verified.',
              explanation: 'ipconfig queries the TCP/IP stack.',
              submitted_at: '2026-09-29T10:02:00Z',
            },
          ],
        }),
      })
    }

    // GET /api/v1/lab-attempts
    if (url.includes('/api/v1/lab-attempts')) {
      return Promise.resolve({
        ok: true,
        json: async () => [
          {
            id: 501,
            lab_id: 1,
            lab_title: 'Find Your Local IPv4 Address',
            lab_slug: 'find-your-local-ipv4-address',
            lab_difficulty: 'BEGINNER',
            lab_environment: 'LOCAL_SYSTEM',
            attempt_number: 1,
            status: 'COMPLETED',
            score: 20,
            total_points: 20,
            percentage: 100,
            started_at: '2026-09-29T10:00:00Z',
            completed_at: '2026-09-29T10:05:00Z',
            time_taken_seconds: 300,
          },
        ],
      })
    }

    // GET /api/v1/labs
    if (url.includes('/api/v1/labs')) {
      return Promise.resolve({
        ok: true,
        json: async () => [mockLabBrief],
      })
    }

    return Promise.resolve({
      ok: true,
      json: async () => ({}),
    })
  })

  global.fetch = mockFetch
})

describe('Step 4 — Hands-on Networking Lab Engine', () => {
  describe('Input Components Suite', () => {
    it('SingleChoiceInput renders options and updates selection', () => {
      const handleChange = vi.fn()
      render(
        <SingleChoiceInput
          options={[
            { id: 'opt1', text: 'Option One' },
            { id: 'opt2', text: 'Option Two' },
          ]}
          value="opt1"
          onChange={handleChange}
        />
      )

      expect(screen.getByText('Option One')).toBeInTheDocument()
      expect(screen.getByText('Option Two')).toBeInTheDocument()

      fireEvent.click(screen.getByText('Option Two'))
      expect(handleChange).toHaveBeenCalledWith('Option Two')
    })

    it('MultipleChoiceInput toggles items', () => {
      const handleChange = vi.fn()
      render(
        <MultipleChoiceInput
          options={[
            { id: 'A', text: 'Alpha' },
            { id: 'B', text: 'Beta' },
          ]}
          value={['Alpha']}
          onChange={handleChange}
        />
      )

      fireEvent.click(screen.getByText('Beta'))
      expect(handleChange).toHaveBeenCalledWith(['Alpha', 'Beta'])
    })

    it('TextInput updates string value', () => {
      const handleChange = vi.fn()
      render(<TextInput value="initial" onChange={handleChange} placeholder="Type value" />)

      const input = screen.getByPlaceholderText('Type value')
      fireEvent.change(input, { target: { value: 'updated value' } })
      expect(handleChange).toHaveBeenCalledWith('updated value')
    })

    it('NumericInput handles numerical entry', () => {
      const handleChange = vi.fn()
      render(<NumericInput value={42} onChange={handleChange} placeholder="Number" />)

      const input = screen.getByPlaceholderText('Number')
      fireEvent.change(input, { target: { value: '80' } })
      expect(handleChange).toHaveBeenCalledWith('80')
    })

    it('IPAddressInput renders input and updates IP', () => {
      const handleChange = vi.fn()
      render(<IPAddressInput value="192.168.1.1" onChange={handleChange} placeholder="Enter IP" />)

      const input = screen.getByPlaceholderText('Enter IP')
      expect(input).toHaveValue('192.168.1.1')

      fireEvent.change(input, { target: { value: '192.168.1.254' } })
      expect(handleChange).toHaveBeenCalledWith('192.168.1.254')
    })

    it('CIDRInput renders input and updates notation', () => {
      const handleChange = vi.fn()
      render(<CIDRInput value="10.0.0.0/24" onChange={handleChange} placeholder="Enter CIDR" />)

      const input = screen.getByPlaceholderText('Enter CIDR')
      expect(input).toHaveValue('10.0.0.0/24')

      fireEvent.change(input, { target: { value: '10.0.0.0/16' } })
      expect(handleChange).toHaveBeenCalledWith('10.0.0.0/16')
    })

    it('PortInput handles port number', () => {
      const handleChange = vi.fn()
      render(<PortInput value={443} onChange={handleChange} placeholder="Enter Port" />)

      const input = screen.getByPlaceholderText('Enter Port')
      expect(input).toHaveValue(443)

      fireEvent.change(input, { target: { value: '8080' } })
      expect(handleChange).toHaveBeenCalledWith('8080')
    })

    it('SubnetInput renders input for subnet mask', () => {
      const handleChange = vi.fn()
      render(<SubnetInput value="255.255.255.0" onChange={handleChange} placeholder="Enter Mask" />)

      const input = screen.getByPlaceholderText('Enter Mask')
      expect(input).toHaveValue('255.255.255.0')

      fireEvent.change(input, { target: { value: '255.255.255.128' } })
      expect(handleChange).toHaveBeenCalledWith('255.255.255.128')
    })

    it('LabAnswerInput dynamically dispatches according to validation type', () => {
      const handleChange = vi.fn()
      render(
        <LabAnswerInput
          validationType="SINGLE_CHOICE"
          config={{
            validation_type: 'SINGLE_CHOICE',
            options: [{ id: 'choice1', text: 'Choice 1' }],
          }}
          value="choice1"
          onChange={handleChange}
        />
      )
      expect(screen.getByText('Choice 1')).toBeInTheDocument()
    })
  })

  describe('Lab Presentation Components', () => {
    it('LabCard renders title, difficulty, environment, and meta', () => {
      render(
        <MemoryRouter>
          <LabCard lab={mockLabBrief} />
        </MemoryRouter>
      )

      expect(screen.getByText('Find Your Local IPv4 Address')).toBeInTheDocument()
      expect(screen.getByText('BEGINNER')).toBeInTheDocument()
      expect(screen.getByText('Local Terminal')).toBeInTheDocument()
      expect(screen.getByText('15 mins')).toBeInTheDocument()
      expect(screen.getByText('2 steps')).toBeInTheDocument()
      expect(screen.getByText('20 pts')).toBeInTheDocument()
      expect(screen.getByText('Resume Lab')).toBeInTheDocument()
    })

    it('LabFilters handles search, difficulty, and clear filters', () => {
      const handleSearch = vi.fn()
      const handleDiff = vi.fn()
      const handleClear = vi.fn()

      render(
        <LabFilters
          searchQuery="ping"
          onSearchChange={handleSearch}
          selectedDifficulty="BEGINNER"
          onDifficultyChange={handleDiff}
          selectedEnvironment="ALL"
          onEnvironmentChange={vi.fn()}
          selectedStatus="ALL"
          onStatusChange={vi.fn()}
          onClearAll={handleClear}
          totalResults={5}
        />
      )

      expect(screen.getByDisplayValue('ping')).toBeInTheDocument()
      expect(screen.getByText('Clear Filters')).toBeInTheDocument()

      fireEvent.click(screen.getByText('Clear Filters'))
      expect(handleClear).toHaveBeenCalled()

      fireEvent.click(screen.getByText('Intermediate'))
      expect(handleDiff).toHaveBeenCalledWith('INTERMEDIATE')
    })

    it('LabStepList renders steps, active step, and score', () => {
      const handleSelectStep = vi.fn()
      render(
        <MemoryRouter>
          <LabStepList lab={mockLabDetail} currentStepIndex={0} onSelectStep={handleSelectStep} />
        </MemoryRouter>
      )

      expect(screen.getByText('Find Your Local IPv4 Address')).toBeInTheDocument()
      expect(screen.getByText('10 / 20 pts (50%)')).toBeInTheDocument()
      expect(screen.getByText('1. Execute Network Configuration Command')).toBeInTheDocument()
      expect(screen.getByText('2. Enter Your Local IPv4 Address')).toBeInTheDocument()

      fireEvent.click(screen.getByText('2. Enter Your Local IPv4 Address'))
      expect(handleSelectStep).toHaveBeenCalledWith(1)
    })

    it('LabInstructions renders commands and platform tabs', () => {
      render(<LabInstructions step={mockStep1} environmentType="LOCAL_SYSTEM" />)

      expect(screen.getByText(/Local Terminal Drill/i)).toBeInTheDocument()
      expect(screen.getByText(/Windows \(CMD \/ PowerShell\)/i)).toBeInTheDocument()
      expect(screen.getByText(/Linux \(Bash \/ Zsh\)/i)).toBeInTheDocument()
      expect(screen.getByText(/macOS \(Terminal\)/i)).toBeInTheDocument()
      expect(screen.getAllByText('ipconfig').length).toBeGreaterThanOrEqual(1)
    })

    it('LabObservation displays expected output note', () => {
      render(<LabObservation observation="Look for IPv4 address line." />)
      expect(screen.getByText('What to Observe in Your Output')).toBeInTheDocument()
      expect(screen.getByText('Look for IPv4 address line.')).toBeInTheDocument()
    })

    it('LabHint toggles hint content on click', () => {
      const handleHintRevealed = vi.fn()
      render(<LabHint hint="Useful hint text" onHintRevealed={handleHintRevealed} />)

      expect(screen.queryByText('Useful hint text')).not.toBeInTheDocument()
      fireEvent.click(screen.getByText('Need a Hint?'))

      expect(screen.getByText('Useful hint text')).toBeInTheDocument()
      expect(handleHintRevealed).toHaveBeenCalled()
    })

    it('LabFeedback renders correct state with points and explanation', () => {
      render(
        <LabFeedback
          result={{
            step_id: 101,
            attempt_id: 501,
            is_correct: true,
            points_earned: 10,
            max_points: 10,
            feedback: 'Well done!',
            explanation: 'Detailed explanation about sockets.',
            attempt_score: 10,
            attempt_total_points: 10,
            attempt_percentage: 100,
            is_lab_completed: true,
          }}
        />
      )

      expect(screen.getByText('Correct!')).toBeInTheDocument()
      expect(screen.getByText('+10 pts')).toBeInTheDocument()
      expect(screen.getByText('Well done!')).toBeInTheDocument()
      expect(screen.getByText('Detailed explanation about sockets.')).toBeInTheDocument()
    })

    it('LabCompletion renders final score, breakdown, and retry action', () => {
      const handleRetry = vi.fn()
      render(
        <MemoryRouter>
          <LabCompletion lab={mockLabDetail} onRetry={handleRetry} />
        </MemoryRouter>
      )

      expect(screen.getByText('Lab Completed!')).toBeInTheDocument()
      expect(screen.getByText('10 / 20')).toBeInTheDocument()
      expect(screen.getByText('Retake Lab')).toBeInTheDocument()

      fireEvent.click(screen.getByText('Retake Lab'))
      expect(handleRetry).toHaveBeenCalled()
    })
  })

  describe('Pages Integration', () => {
    it('LabsPage loads telemetry and lab catalog', async () => {
      await act(async () => {
        render(
          <MemoryRouter>
            <LabsPage />
          </MemoryRouter>
        )
      })

      expect(screen.getByText('Interactive Networking Labs')).toBeInTheDocument()
      expect(screen.getByText('Available Labs')).toBeInTheDocument()
      expect(screen.getByText('Find Your Local IPv4 Address')).toBeInTheDocument()
    })

    it('LabDetailPage provisions workspace and submits answer', async () => {
      await act(async () => {
        render(
          <MemoryRouter initialEntries={['/labs/find-your-local-ipv4-address']}>
            <Routes>
              <Route path="/labs/:labSlug" element={<LabDetailPage />} />
            </Routes>
          </MemoryRouter>
        )
      })

      // Check step is rendered
      expect(screen.getByText('Enter Your Local IPv4 Address')).toBeInTheDocument()

      // Enter answer in input
      const input = screen.getByPlaceholderText('192.168.1.100')
      fireEvent.change(input, { target: { value: '192.168.1.50' } })

      // Submit an answer
      const submitBtn = screen.getByText('Verify & Submit Answer')
      await act(async () => {
        fireEvent.click(submitBtn)
      })

      // Validation feedback transitions to LabCompletion since all steps are finished
      expect(await screen.findByText('Lab Completed!')).toBeInTheDocument()
      expect(screen.getByText('20 / 20')).toBeInTheDocument()
      expect(screen.getByText('Accuracy')).toBeInTheDocument()
    })

    it('LabHistoryPage displays past attempts and allows viewing breakdown', async () => {
      await act(async () => {
        render(
          <MemoryRouter>
            <LabHistoryPage />
          </MemoryRouter>
        )
      })

      expect(screen.getByText('Lab Attempt History')).toBeInTheDocument()
      expect(screen.getByText('#1')).toBeInTheDocument()
      expect(screen.getByText('Review')).toBeInTheDocument()

      // Click Review
      await act(async () => {
        fireEvent.click(screen.getByText('Review'))
      })

      expect(await screen.findByText('Submitted Step Responses')).toBeInTheDocument()
      expect(screen.getByText('Step 1: Execute Network Configuration Command')).toBeInTheDocument()
    })
  })
})
