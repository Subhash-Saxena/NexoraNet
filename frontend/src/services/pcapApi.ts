import type {
  BookmarkCreateRequest,
  BookmarkItem,
  CaptureDetail,
  CaptureStatistics,
  CaptureSummary,
  ConversationItem,
  EndpointItem,
  FindingCreateRequest,
  FindingItem,
  InvestigationReport,
  NoteCreateRequest,
  NoteItem,
  ObservationItem,
  PacketListResponse,
  ParsedPacketDetail,
  PortItem,
  TimelineBucketItem,
} from '../types/pcap'
import { getApiBaseUrl } from './apiConfig'

class PcapApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  async listCaptures(): Promise<CaptureSummary[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/packet-analysis/captures`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch captures (${res.status})`)
    }
    return res.json()
  }

  async getCapture(captureId: number): Promise<CaptureDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch capture ${captureId} (${res.status})`)
    }
    return res.json()
  }

  async uploadCapture(file: File, name?: string, description?: string): Promise<CaptureDetail> {
    const formData = new FormData()
    formData.append('file', file)

    const params = new URLSearchParams()
    if (name) params.append('name', name)
    if (description) params.append('description', description)

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/packet-analysis/captures${query}`, {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Upload failed (${res.status})`)
    }
    return res.json()
  }

  async reparseCapture(captureId: number): Promise<CaptureDetail> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/reparse`,
      {
        method: 'POST',
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Reparse failed (${res.status})`)
    }
    return res.json()
  }

  async deleteCapture(captureId: number): Promise<{ message: string }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}`, {
      method: 'DELETE',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Delete failed (${res.status})`)
    }
    return res.json()
  }

  async getPackets(
    captureId: number,
    options?: { filter?: string; page?: number; pageSize?: number }
  ): Promise<PacketListResponse> {
    const params = new URLSearchParams()
    if (options?.filter && options.filter.trim()) params.append('filter', options.filter.trim())
    if (options?.page) params.append('page', String(options.page))
    if (options?.pageSize) params.append('page_size', String(options.pageSize))

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/packets${query}`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch packets (${res.status})`)
    }
    return res.json()
  }

  async getPacketDetail(captureId: number, packetNumber: number): Promise<ParsedPacketDetail> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/packets/${packetNumber}`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load packet #${packetNumber}`)
    }
    return res.json()
  }

  async getStatistics(captureId: number): Promise<CaptureStatistics> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/statistics`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load statistics (${res.status})`)
    }
    return res.json()
  }

  async getConversations(captureId: number): Promise<ConversationItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/conversations`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load conversations (${res.status})`)
    }
    return res.json()
  }

  async getEndpoints(captureId: number): Promise<EndpointItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/endpoints`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load endpoints (${res.status})`)
    }
    return res.json()
  }

  async getPorts(captureId: number): Promise<PortItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/ports`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load ports (${res.status})`)
    }
    return res.json()
  }

  async getTimeline(captureId: number, bucketCount: number = 30): Promise<TimelineBucketItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/timeline?bucket_count=${bucketCount}`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load timeline (${res.status})`)
    }
    return res.json()
  }

  async getObservations(captureId: number): Promise<ObservationItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/observations`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load observations (${res.status})`)
    }
    return res.json()
  }

  async createBookmark(captureId: number, data: BookmarkCreateRequest): Promise<BookmarkItem> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/bookmarks`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data),
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create bookmark (${res.status})`)
    }
    return res.json()
  }

  async listBookmarks(captureId: number): Promise<BookmarkItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/bookmarks`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch bookmarks (${res.status})`)
    }
    return res.json()
  }

  async deleteBookmark(captureId: number, bookmarkId: number): Promise<{ message: string }> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/bookmarks/${bookmarkId}`,
      {
        method: 'DELETE',
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to delete bookmark (${res.status})`)
    }
    return res.json()
  }

  async createNote(captureId: number, data: NoteCreateRequest): Promise<NoteItem> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/notes`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data),
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create note (${res.status})`)
    }
    return res.json()
  }

  async listNotes(captureId: number): Promise<NoteItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/notes`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch notes (${res.status})`)
    }
    return res.json()
  }

  async createFinding(captureId: number, data: FindingCreateRequest): Promise<FindingItem> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/findings`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data),
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to save finding (${res.status})`)
    }
    return res.json()
  }

  async listFindings(captureId: number): Promise<FindingItem[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/findings`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch findings (${res.status})`)
    }
    return res.json()
  }

  async getReport(captureId: number): Promise<InvestigationReport> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/packet-analysis/captures/${captureId}/report`,
      {
        headers: { Accept: 'application/json' },
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to load report (${res.status})`)
    }
    return res.json()
  }
}

export const pcapApi = new PcapApiService()
