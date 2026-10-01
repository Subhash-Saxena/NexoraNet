import React, { useState, useRef } from 'react'
import { UploadCloud, AlertCircle, ShieldAlert, CheckCircle2, Loader2 } from 'lucide-react'
import { pcapApi } from '../../services/pcapApi'
import type { CaptureDetail } from '../../types/pcap'

interface CaptureUploaderProps {
  onUploadSuccess: (capture: CaptureDetail) => void
  onCancel?: () => void
}

export const CaptureUploader: React.FC<CaptureUploaderProps> = ({ onUploadSuccess, onCancel }) => {
  const [file, setFile] = useState<File | null>(null)
  const [customName, setCustomName] = useState('')
  const [description, setDescription] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const validateFile = (selectedFile: File): boolean => {
    const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase()
    if (!['.pcap', '.pcapng', '.cap'].includes(ext)) {
      setError(`Invalid format "${ext}". Please provide a .pcap or .pcapng file.`)
      return false
    }
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('File exceeds maximum upload limit of 50 MB.')
      return false
    }
    setError(null)
    return true
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0]
      if (validateFile(dropped)) {
        setFile(dropped)
        if (!customName) {
          setCustomName(dropped.name.replace(/\.[^/.]+$/, ''))
        }
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      if (validateFile(selected)) {
        setFile(selected)
        if (!customName) {
          setCustomName(selected.name.replace(/\.[^/.]+$/, ''))
        }
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a PCAP file to upload.')
      return
    }

    try {
      setIsUploading(true)
      setError(null)
      const capture = await pcapApi.uploadCapture(file, customName || undefined, description || undefined)
      onUploadSuccess(capture)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed'
      setError(msg)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="pcap-uploader-card" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '10px', padding: '1.5rem' }}>
      <div className="pcap-notice-banner safety" style={{ marginBottom: '1.25rem' }}>
        <ShieldAlert size={20} style={{ flexShrink: 0 }} />
        <div>
          <strong>Offline Defensive Environment:</strong> Captures are analyzed purely offline. NexoraNet will never replay, transmit, or execute captured traffic payloads.
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div
          className={`pcap-dropzone ${dragActive ? 'dragging' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pcap,.pcapng,.cap"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <UploadCloud size={36} color="#38bdf8" />
          <div>
            <span style={{ color: '#fff', fontWeight: 600 }}>Click to browse</span> or drag and drop PCAP capture here
          </div>
          <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
            Supported formats: <strong>.pcap</strong>, <strong>.pcapng</strong>, <strong>.cap</strong> (Max 50 MB)
          </div>
          {file && (
            <div style={{ marginTop: '0.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: '#10b981', background: 'rgba(16, 185, 129, 0.1)', padding: '0.3rem 0.75rem', borderRadius: '4px', fontSize: '0.8125rem' }}>
              <CheckCircle2 size={16} /> Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </div>
          )}
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8125rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
            Capture Title (Optional)
          </label>
          <input
            type="text"
            className="pcap-filter-input"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            placeholder="e.g. Suspicious Web Traffic Investigation"
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.8125rem', color: '#94a3b8', marginBottom: '0.35rem' }}>
            Investigation Notes / Context
          </label>
          <textarea
            className="pcap-filter-input"
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe what incident or lab scenario this capture represents..."
            style={{ resize: 'vertical' }}
          />
        </div>

        {error && (
          <div className="pcap-notice-banner danger">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
          {onCancel && (
            <button
              type="button"
              className="pcap-page-btn"
              onClick={onCancel}
              disabled={isUploading}
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            className="pcap-filter-apply-btn"
            disabled={!file || isUploading}
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            {isUploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Parsing PCAP Layers...
              </>
            ) : (
              'Upload & Inspect'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
