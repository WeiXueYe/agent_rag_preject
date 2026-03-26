import { NavBar } from "@/components/navigation-bar/navbar";
import AgentManager from "@/components/agent-list/agent-manager";
import Content from "@/components/content";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-gray-50">
      <NavBar />

      <AgentManager>
        <Content />
      </AgentManager>
      
    </main>
    
  );
}
