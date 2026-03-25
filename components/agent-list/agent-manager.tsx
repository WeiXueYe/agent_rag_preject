'use client'

import { useState, createContext, useContext, useCallback } from 'react'
import { Agent, updateAgent, getAgents } from '@/lib/agent'

interface AgentContextType {
  selectedAgent: Agent | null
  setSelectedAgent: (agent: Agent | null) => void
  handleUpdate: (agent: Agent) => Promise<void>
  handleCancelEdit: () => void
  sendAgentInfoToBackend: (agent: Agent) => Promise<void>
  agents: Agent[]
  refreshAgents: () => Promise<void>
}

const AgentContext = createContext<AgentContextType | undefined>(undefined)

export function useAgentContext() {
  const context = useContext(AgentContext)
  if (!context) {
    throw new Error('useAgentContext must be used within AgentManager')
  }
  return context
}

export default function AgentManager({ children }: { children: React.ReactNode }) {
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])

  const refreshAgents = useCallback(async () => {
    try {
      const data = await getAgents()
      setAgents(data || [])
    } catch (err) {
      console.error('获取 agents 失败:', err)
    }
  }, [])

  const handleUpdate = async (updatedAgent: Agent) => {
    try {
      await updateAgent(updatedAgent)
      setSelectedAgent(updatedAgent)
      await refreshAgents()
    } catch (err) {
      console.error('更新 agent 失败:', err)
    }
  }

  const handleCancelEdit = () => {
    setSelectedAgent(null)
  }

  const sendAgentInfoToBackend = async (agent: Agent) => {
    try {
      // 直接使用 Supabase API 更新 agent 信息
      await updateAgent(agent)
      console.log('Agent info updated successfully:', agent)
    } catch (err) {
      console.error('更新 agent 信息失败:', err)
    }
  }

  return (
    <AgentContext.Provider value={{ selectedAgent, setSelectedAgent, handleUpdate, handleCancelEdit, sendAgentInfoToBackend, agents, refreshAgents }}>
      {children}
    </AgentContext.Provider>
  )
}