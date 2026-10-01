import type {
  Scenario,
  ScenarioValidationResult,
  SimulationResult,
  TopologyData,
  TopologyResponse,
} from '../types/simulator'
import { getApiBaseUrl } from './apiConfig'

class SimulatorApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  async getTopologies(): Promise<TopologyResponse[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/topologies`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to fetch topologies`)
    }
    return response.json()
  }

  async getTopology(idOrSlug: string): Promise<TopologyResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/topologies/${idOrSlug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to fetch topology ${idOrSlug}`)
    }
    return response.json()
  }

  async createTopology(data: {
    name: string
    description?: string
    difficulty?: string
    topology_data: TopologyData
  }): Promise<TopologyResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/topologies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to save topology`)
    }
    return response.json()
  }

  async updateTopology(
    id: number,
    data: {
      name?: string
      description?: string
      difficulty?: string
      topology_data?: TopologyData
    }
  ): Promise<TopologyResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/topologies/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to update topology`)
    }
    return response.json()
  }

  async deleteTopology(id: number): Promise<void> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/topologies/${id}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to delete topology`)
    }
  }

  async validateTopology(data: TopologyData): Promise<{
    is_valid: boolean
    errors: string[]
    warnings: string[]
    subnets_detected: any[]
  }> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/topologies/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to validate topology`)
    }
    return response.json()
  }

  async simulatePacket(req: {
    topology: TopologyData
    source_device_id: string
    destination_device_id?: string
    destination_ip?: string
    protocol?: string
    tcp_flags?: string[]
    dns_query_name?: string
    port?: number
  }): Promise<SimulationResult> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/simulate/packet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(req),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${response.status}: Simulation error`)
    }
    return response.json()
  }

  async getScenarios(): Promise<Scenario[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/scenarios`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to fetch scenarios`)
    }
    return response.json()
  }

  async getScenario(slug: string): Promise<Scenario> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/scenarios/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to fetch scenario ${slug}`)
    }
    return response.json()
  }

  async validateScenario(
    slug: string,
    req: {
      topology: TopologyData
      hints_used?: number
    }
  ): Promise<ScenarioValidationResult> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/simulator/scenarios/${slug}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(req),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${response.status}: Failed to validate scenario`)
    }
    return response.json()
  }
}

export const simulatorApi = new SimulatorApiService()
