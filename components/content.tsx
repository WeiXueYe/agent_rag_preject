'use client'

import { useState } from "react";
import { OuterFrameContainer, OuterFrameItem } from "@/components/frame/outer-frame";
import ChatDialog from "@/components/chat-model/chat-dialog";
import ListView from "@/components/agent-list/list-view";
import AgentUpdate from "@/components/agent-list/agent-update";
import RagSubmit from "@/components/rag-model/rag-submit";
import RagList from "@/components/rag-model/rag-list";
import { useAgentContext } from "@/components/agent-list/agent-manager";

export default function Content() {
  const { isEditing } = useAgentContext();
  const [refreshKey, setRefreshKey] = useState(0);
  
  const handleRefreshFiles = () => {
    setRefreshKey(prev => prev + 1);
  };
  
  return (
    <OuterFrameContainer className="flex-1 min-h-0">
      <OuterFrameItem>
        <h3 className="font-bold mb-2">选择项目</h3>
        <ListView />
      </OuterFrameItem>

      <OuterFrameItem className="flex flex-col">
        <h3 className="font-bold mb-2">模型对话</h3>
        <ChatDialog className="flex-1" />
      </OuterFrameItem>

      <OuterFrameItem>
        {isEditing?(
          <h3 className="font-bold mb-2">助手编辑</h3>
        ):(
          <h3 className="font-bold mb-2">文件管理</h3>
        )}
        {isEditing ? (
          <AgentUpdate />
        ) : (
          <div className="space-y-4">
            <RagSubmit onSuccess={handleRefreshFiles} />
            <div>
              <h4 className="font-medium mb-2">已上传文件</h4>
              <RagList key={refreshKey} />
            </div>
          </div>
        )}
      </OuterFrameItem>
    </OuterFrameContainer>
  );
}
