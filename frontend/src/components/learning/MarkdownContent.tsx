import React, { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { OSIStackDiagram } from './diagrams/OSIStackDiagram'
import { TCPHandshakeDiagram } from './diagrams/TCPHandshakeDiagram'
import { DNSResolutionDiagram } from './diagrams/DNSResolutionDiagram'
import { DHCPSequenceDiagram } from './diagrams/DHCPSequenceDiagram'
import { EncapsulationDiagram } from './diagrams/EncapsulationDiagram'
import { CalloutCard } from './CalloutCard'

export interface MarkdownContentProps {
  content: string
}

export const MarkdownContent: React.FC<MarkdownContentProps> = ({ content }) => {
  if (!content) return null

  // Split content into blocks
  const lines = content.split('\n')
  const blocks: React.ReactNode[] = []

  let inCodeBlock = false
  let codeLang = ''
  let codeBuffer: string[] = []

  let inTable = false
  let tableHeader: string[] = []
  let tableRows: string[][] = []

  let listBuffer: string[] = []
  let listType: 'ul' | 'ol' | null = null

  let quoteBuffer: string[] = []
  let quoteType: 'note' | 'warning' | 'security' | 'interview' | 'technical' | 'default' = 'default'

  const flushList = () => {
    if (listBuffer.length > 0 && listType) {
      const items = [...listBuffer]
      const currentListType = listType
      blocks.push(
        currentListType === 'ul' ? (
          <ul key={`list-${blocks.length}`} style={{ margin: '14px 0 18px 24px' }}>
            {items.map((item, i) => (
              <li key={i} dangerouslySetInnerHTML={{ __html: formatInline(item) }} />
            ))}
          </ul>
        ) : (
          <ol key={`list-${blocks.length}`} style={{ margin: '14px 0 18px 24px' }}>
            {items.map((item, i) => (
              <li key={i} dangerouslySetInnerHTML={{ __html: formatInline(item) }} />
            ))}
          </ol>
        )
      )
      listBuffer = []
      listType = null
    }
  }

  const flushTable = () => {
    if (inTable && tableHeader.length > 0) {
      blocks.push(
        <div key={`table-${blocks.length}`} style={{ overflowX: 'auto', margin: '20px 0' }}>
          <table>
            <thead>
              <tr>
                {tableHeader.map((th, i) => (
                  <th key={i} dangerouslySetInnerHTML={{ __html: formatInline(th) }} />
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, rIdx) => (
                <tr key={rIdx}>
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} dangerouslySetInnerHTML={{ __html: formatInline(cell) }} />
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
      inTable = false
      tableHeader = []
      tableRows = []
    }
  }

  const flushQuote = () => {
    if (quoteBuffer.length > 0) {
      const text = quoteBuffer.join('\n')
      let calloutType: 'bca_simple' | 'technical' | 'security' | 'interview' = 'bca_simple'
      let title = 'Educational Note'

      if (quoteType === 'security' || quoteType === 'warning') {
        calloutType = 'security'
        title = 'Security & Threat Relevance'
      } else if (quoteType === 'technical') {
        calloutType = 'technical'
        title = 'Technical Deep-Dive'
      } else if (quoteType === 'interview') {
        calloutType = 'interview'
        title = 'Exam & Interview Note'
      } else {
        calloutType = 'bca_simple'
        title = 'BCA Simple Concept'
      }

      blocks.push(
        <CalloutCard
          key={`quote-${blocks.length}`}
          type={calloutType}
          title={title}
          content={text}
        />
      )
      quoteBuffer = []
      quoteType = 'default'
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i]
    const trimmed = rawLine.trim()

    // 1. Code Blocks
    if (trimmed.startsWith('```')) {
      if (inCodeBlock) {
        // Close code block
        const codeText = codeBuffer.join('\n')
        blocks.push(<CodeBlockRenderer key={`code-${blocks.length}`} code={codeText} lang={codeLang} />)
        codeBuffer = []
        inCodeBlock = false
        codeLang = ''
        continue
      } else {
        flushList()
        flushTable()
        flushQuote()
        inCodeBlock = true
        codeLang = trimmed.substring(3).trim()
        codeBuffer = []
        continue
      }
    }

    if (inCodeBlock) {
      codeBuffer.push(rawLine)
      continue
    }

    // 2. Diagrams Shortcode
    if (trimmed.startsWith('[DIAGRAM:') && trimmed.endsWith(']')) {
      flushList()
      flushTable()
      flushQuote()
      const diagramName = trimmed.substring(9, trimmed.length - 1).trim()
      blocks.push(<DiagramShortcodeRenderer key={`diag-${blocks.length}`} name={diagramName} />)
      continue
    }

    // 3. Blockquotes & Callouts
    if (trimmed.startsWith('>')) {
      flushList()
      flushTable()
      const quoteText = trimmed.substring(1).trim()

      if (quoteText.startsWith('[!NOTE]') || quoteText.startsWith('[!BCA]')) {
        quoteType = 'note'
        continue
      } else if (quoteText.startsWith('[!WARNING]') || quoteText.startsWith('[!SECURITY]')) {
        quoteType = 'security'
        continue
      } else if (quoteText.startsWith('[!TECHNICAL]') || quoteText.startsWith('[!DEEP-DIVE]')) {
        quoteType = 'technical'
        continue
      } else if (quoteText.startsWith('[!INTERVIEW]') || quoteText.startsWith('[!EXAM]') || quoteText.startsWith('[!TIP]')) {
        quoteType = 'interview'
        continue
      }

      quoteBuffer.push(quoteText)
      continue
    } else if (quoteBuffer.length > 0) {
      flushQuote()
    }

    // 4. Tables
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushList()
      const cells = trimmed
        .substring(1, trimmed.length - 1)
        .split('|')
        .map((c) => c.trim())

      // Skip separator row |---|---|
      if (cells.every((c) => /^:?-+:?$/.test(c))) {
        continue
      }

      if (!inTable) {
        inTable = true
        tableHeader = cells
      } else {
        tableRows.push(cells)
      }
      continue
    } else if (inTable) {
      flushTable()
    }

    // 5. Lists (unordered & ordered)
    const ulMatch = trimmed.match(/^[-*]\s+(.*)$/)
    const olMatch = trimmed.match(/^(\d+)\.\s+(.*)$/)

    if (ulMatch) {
      if (listType !== 'ul') {
        flushList()
        listType = 'ul'
      }
      listBuffer.push(ulMatch[1])
      continue
    } else if (olMatch) {
      if (listType !== 'ol') {
        flushList()
        listType = 'ol'
      }
      listBuffer.push(olMatch[2])
      continue
    } else if (listBuffer.length > 0) {
      flushList()
    }

    // 6. Blank Lines
    if (trimmed === '') {
      continue
    }

    // 7. Headings
    if (trimmed.startsWith('# ')) {
      blocks.push(
        <h1 key={`h1-${blocks.length}`} id={`heading-${blocks.length}`}>
          {trimmed.substring(2)}
        </h1>
      )
      continue
    }
    if (trimmed.startsWith('## ')) {
      blocks.push(
        <h2 key={`h2-${blocks.length}`} id={`heading-${blocks.length}`}>
          {trimmed.substring(3)}
        </h2>
      )
      continue
    }
    if (trimmed.startsWith('### ')) {
      blocks.push(
        <h3 key={`h3-${blocks.length}`} id={`heading-${blocks.length}`}>
          {trimmed.substring(4)}
        </h3>
      )
      continue
    }
    if (trimmed.startsWith('#### ')) {
      blocks.push(
        <h4 key={`h4-${blocks.length}`} style={{ fontSize: '1rem', fontWeight: 600, color: '#e2e8f0', margin: '18px 0 8px' }}>
          {trimmed.substring(5)}
        </h4>
      )
      continue
    }

    // 8. Horizontal Rule
    if (/^---|\*\*\*|___$/.test(trimmed)) {
      blocks.push(<hr key={`hr-${blocks.length}`} style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '32px 0' }} />)
      continue
    }

    // 9. Standard Paragraph
    blocks.push(
      <p
        key={`p-${blocks.length}`}
        dangerouslySetInnerHTML={{ __html: formatInline(rawLine) }}
      />
    )
  }

  // Cleanup any trailing buffers
  flushList()
  flushTable()
  flushQuote()
  if (inCodeBlock && codeBuffer.length > 0) {
    blocks.push(<CodeBlockRenderer key={`code-${blocks.length}`} code={codeBuffer.join('\n')} lang={codeLang} />)
  }

  return <div className="lesson-content">{blocks}</div>
}

function formatInline(text: string): string {
  if (!text) return ''

  return text
    // Escapes
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Inline code `code`
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold **text**
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Italic *text*
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Links [title](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: var(--cyan-primary); text-decoration: underline;">$1</a>')
}

const CodeBlockRenderer: React.FC<{ code: string; lang: string }> = ({ code, lang }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{ position: 'relative', margin: '20px 0' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#0a101f',
          borderTop: '1px solid var(--border-color)',
          borderLeft: '1px solid var(--border-color)',
          borderRight: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md) var(--radius-md) 0 0',
          padding: '6px 14px',
          fontSize: '0.74rem',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)',
        }}
      >
        <span>{lang ? lang.toUpperCase() : 'CODE'}</span>
        <button
          onClick={handleCopy}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          {copied ? <Check size={12} color="var(--emerald-success)" /> : <Copy size={12} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <pre style={{ margin: 0, borderRadius: '0 0 var(--radius-md) var(--radius-md)' }}>
        <code>{code}</code>
      </pre>
    </div>
  )
}

const DiagramShortcodeRenderer: React.FC<{ name: string }> = ({ name }) => {
  switch (name) {
    case 'osi_stack':
      return <OSIStackDiagram />
    case 'tcp_handshake':
      return <TCPHandshakeDiagram />
    case 'dns_resolution':
      return <DNSResolutionDiagram />
    case 'dhcp_sequence':
      return <DHCPSequenceDiagram />
    case 'encapsulation':
      return <EncapsulationDiagram />
    default:
      return (
        <div style={{ padding: '16px', border: '1px dashed var(--border-color)', borderRadius: 'var(--radius-sm)', textAlign: 'center', color: 'var(--text-muted)' }}>
          Diagram placeholder: [{name}]
        </div>
      )
  }
}
