'use client'

import { Agent } from '@/lib/agent'

interface AgentItemProps {
  agent: Agent
  onDelete: (id: number) => void
  onClick: (id: number) => void
  isSelected: boolean
}

export default function AgentItem({
  agent,
  onDelete,
  onClick,
  isSelected
}: AgentItemProps) {
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete(agent.id!)
  }

  return (
    <div 
      className={`p-4 border-b border-gray-200 cursor-pointer transition-colors ${
        isSelected ? 'bg-blue-100' : 'hover:bg-gray-50'
      }`}
      onClick={() => onClick(agent.id!)}
    >
      <div className="flex justify-between items-center">
        <div>
          <h3 className="font-medium text-lg">{agent.agent_name}</h3>
          <p className="text-xs text-gray-500 mt-1">
            创建时间: {new Date(agent.created_at || '').toLocaleString()}
          </p>
        </div>
        <button
          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
          onClick={handleDeleteClick}
        >
          删除
        </button>
      </div>
    </div>
  )
}