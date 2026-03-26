'use client'

import { Agent } from '@/lib/agent'

interface AgentItemProps {
  agent: Agent
  onEdit: (id: number) => void
  onClick: (id: number) => void
  isSelected: boolean
}

export default function AgentItem({
  agent,
  onEdit,
  onClick,
  isSelected
}: AgentItemProps) {
  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit(agent.id!)
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
          className="px-3 py-1 bg-white text-gray-800 border border-gray-300 rounded hover:bg-gray-50"
          onClick={handleEditClick}
        >
          编辑
        </button>
      </div>
    </div>
  )
}