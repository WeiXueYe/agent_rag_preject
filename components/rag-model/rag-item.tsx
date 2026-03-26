'use client'

import React from 'react'

interface RagItemProps {
  id: number
  fileTitle: string
  fileType: string
  createdAt: string
  onDelete: (id: number) => void
}

export default function RagItem({ id, fileTitle, fileType, createdAt, onDelete }: RagItemProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete(id)
  }

  return (
    <div className="flex justify-between items-center p-3 border-b border-gray-200 hover:bg-gray-50">
      <div>
        <h4 className="font-medium text-gray-800">{fileTitle}</h4>
        <p className="text-xs text-gray-500">
          {fileType} · {new Date(createdAt).toLocaleString()}
        </p>
      </div>
      <button
        className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
        onClick={handleDelete}
      >
        删除
      </button>
    </div>
  )
}
