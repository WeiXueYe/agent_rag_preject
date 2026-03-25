import { OuterFrameContainer, OuterFrameItem } from "@/components/frame/outer-frame";
import { NavBar } from "@/components/navigation-bar/navbar";
import ChatDialog from "@/components/chat-model/chat-dialog";
import AgentManager from "@/components/agent-list/agent-manager";
import ListView from "@/components/agent-list/list-view";
import AgentUpdate from "@/components/agent-list/agent-update";
import RagSubmit from "@/components/rag-model/rag-submit";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-gray-50">
      <NavBar />

      <AgentManager>
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
            <h3 className="font-bold mb-2">助手编辑</h3>
            <AgentUpdate />
            <RagSubmit />
          </OuterFrameItem>
        </OuterFrameContainer>
      </AgentManager>
      
    </main>
    
  );
}
