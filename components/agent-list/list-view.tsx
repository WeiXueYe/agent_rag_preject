'use client'

import { useState, useEffect } from 'react'
import { Agent, createAgent, deleteAgent } from '@/lib/agent'
import AgentItem from './agent-item'
import { useAgentContext } from './agent-manager'

export default function ListView() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null)
  const { setSelectedAgent, sendAgentInfoToBackend, agents, refreshAgents } = useAgentContext()

  // 加载 agents 列表
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true)
        await refreshAgents()
      } catch (err) {
        console.error('获取 agents 失败:', err)
        setError('获取 agents 失败')
      } finally {
        setLoading(false)
      }
    }

    fetchAgents() 
  }, [refreshAgents])

  // 新建 agent
  const handleCreateAgent = async () => {
    try {
      await createAgent()
      await refreshAgents()
      console.log('点击 创建 agent ')
    } catch (err) {
      console.error('创建 agent 失败:', err)
      setError('创建 agent 失败')
    }
  }

  // 删除 agent
  const handleDeleteAgent = async (id: number) => {
    try {
      await deleteAgent(id)
      await refreshAgents()
      if (selectedAgentId === id) {
        setSelectedAgentId(null)
      }
    } catch (err) {
      console.error('删除 agent 失败:', err)
      setError('删除 agent 失败')
    }
  }

  // 处理列表项点击
  const handleAgentClick = async (id: number) => {
    setSelectedAgentId(id)
    const agent = agents.find(a => a.id === id)
    if (agent) {
      setSelectedAgent(agent)
      await sendAgentInfoToBackend(agent)
    }
    console.log('Selected agent ID:', id)
  }

  if (loading) {
    return <div className="p-4">加载中...</div>
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>
  }

  return (
    <div className="w-full">
      {/* 列表栏 */}
      <div className="border border-gray-200 rounded-t-lg h-[610px] overflow-y-auto">
        {agents.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            暂无助手，请点击下方按钮创建
          </div>
        ) : (
          agents.map(agent => (
            <AgentItem
              key={agent.id}
              agent={agent}
              onDelete={handleDeleteAgent}
              onClick={handleAgentClick}
              isSelected={selectedAgentId === agent.id}
            />
          ))
        )}
      </div>

      {/* 新建按钮 */}
      <div className="mt-4 flex justify-center">
        <button
          className="w-32 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
          onClick={handleCreateAgent}
        >
          新建助手
        </button>
      </div>
    </div>
  )
}