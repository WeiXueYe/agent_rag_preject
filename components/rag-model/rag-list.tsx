'use client'

import { useState, useEffect } from 'react'
import { useAgentContext } from '@/components/agent-list/agent-manager'
import RagItem from './rag-item'
import { createClient } from '@/lib/supabase/client'

interface RagFile {
  id: number
  created_at: string
  user_id: string
  agent_id: number
  file_title: string
  file_type: string
}

interface RagListProps {
  onRefresh?: () => void
}

export default function RagList({ onRefresh }: RagListProps) {
  const { selectedAgent } = useAgentContext()
  const [files, setFiles] = useState<RagFile[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const supabase = createClient()

  // 获取文件列表
  const fetchFiles = async () => {
    if (!selectedAgent) return

    setLoading(true)
    setError(null)
    try {
      const { data, error } = await supabase
        .from('rag_files')
        .select('*')
        .eq('agent_id', selectedAgent.id)

      if (error) {
        throw new Error(`获取文件列表失败: ${error.message}`)
      }

      setFiles(data || [])
    } catch (err) {
      console.error("获取文件列表错误:", err)
      setError(err instanceof Error ? err.message : "未知错误")
    } finally {
      setLoading(false)
    }
  }

  // 当selectedAgent改变时，重新获取文件列表
  useEffect(() => {
    fetchFiles()
  }, [selectedAgent, supabase])

  // 删除文件
  const handleDeleteFile = async (id: number) => {
    try {
      // 删除文件记录
      const { error: deleteError } = await supabase
        .from('rag_files')
        .delete()
        .eq('id', id)

      if (deleteError) {
        throw new Error(`删除文件失败: ${deleteError.message}`)
      }

      // 同时删除相关的向量数据
      await supabase
        .from('rag_vec')
        .delete()
        .eq('file_id', id)

      // 重新获取文件列表
      fetchFiles()
    } catch (err) {
      console.error("删除文件错误:", err)
      setError(err instanceof Error ? err.message : "未知错误")
    }
  }

  if (!selectedAgent) {
    return (
      <div className="p-4 text-center text-gray-500">
        请选择一个Agent以查看文件列表
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-4 text-center">
        加载文件列表中...
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-500">
        {error}
      </div>
    )
  }

  if (files.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        暂无文件
      </div>
    )
  }

  return (
    <div className="border border-gray-200 rounded-md">
      {files.map((file) => (
        <RagItem
          key={file.id}
          id={file.id}
          fileTitle={file.file_title}
          fileType={file.file_type}
          createdAt={file.created_at}
          onDelete={handleDeleteFile}
        />
      ))}
    </div>
  )
}
