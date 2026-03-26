'use client'

import { useState, useEffect } from 'react'
import { Agent } from '@/lib/agent'
import { useAgentContext } from './agent-manager'

export default function AgentUpdate() {
  const { editingAgent, handleUpdate, handleDelete, handleCancelEdit, sendAgentInfoToBackend } = useAgentContext()
  const [agentName, setAgentName] = useState('')
  const [prompt, setPrompt] = useState('')

  useEffect(() => {
    if (editingAgent) {
      setAgentName(editingAgent.agent_name)
      setPrompt(editingAgent.prompt)
    }
  }, [editingAgent])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (editingAgent) {
      const updatedAgent = {
        ...editingAgent,
        agent_name: agentName,
        prompt: prompt
      }
      await handleUpdate(updatedAgent)
      await sendAgentInfoToBackend(updatedAgent)
    }
  }

  if (!editingAgent) {
    return (
      <div className="p-4 text-center text-gray-500">
        请选择一个助手进行编辑
      </div>
    )
  }

  return (
    <div className="p-4">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">助手名称</label>
          <input
            type="text"
            value={agentName}
            onChange={(e) => setAgentName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">提示词</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[200px]"
            required
          />
        </div>

        <div className="flex space-x-2">
          <button
            type="submit"
            className="flex-1 px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
          >
            保存
          </button>
          <button
            type="button"
            onClick={handleCancelEdit}
            className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
          >
            取消
          </button>
          <button
            type="button"
            onClick={() => editingAgent && handleDelete(editingAgent.id!)}
            className="flex-1 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            删除
          </button>
        </div>
      </form>
    </div>
  )
}