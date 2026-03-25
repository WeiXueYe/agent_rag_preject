"use client";

import { useState, useEffect } from "react";
import { getJwtToken } from "@/app/auth/get-info/get-jwt";
import MessageList from "./message-list";
import InputArea from "./input-area";
import { useAgentContext } from "../agent-list/agent-manager";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

interface ChatDialogProps {
  className?: string;
}

export default function ChatDialog({ className = "" }: ChatDialogProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [isGeneratingResponse, setIsGeneratingResponse] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { selectedAgent } = useAgentContext();

  // 当选中的助手改变时，获取该助手的历史消息
  useEffect(() => {
    if (selectedAgent) {
      fetchRecentMessages();
    } else {
      // 如果没有选中助手，清空消息列表
      setMessages([]);
    }
  }, [selectedAgent]);

  // 获取历史消息的函数
  const fetchRecentMessages = async () => {
    if (!selectedAgent) return;

    setIsLoadingMessages(true);
    setError(null);

    try {
      const jwtToken = await getJwtToken();
      if (!jwtToken) {
        throw new Error("无法获取 JWT 令牌，请先登录");
      }

      const response = await fetch("http://localhost:8000/recent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          prompt: "",
          agent_id: selectedAgent.id,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("认证失败，请重新登录");
        }
        throw new Error(`请求失败: ${response.status}`);
      }

      const data = await response.json();

      // 转换历史消息格式
      const formattedMessages: Message[] = data.map((msg: any) => ({
        role: msg.role === "user" ? "user" : "assistant",
        content: msg.content,
        timestamp: new Date(),
      }));

      setMessages(formattedMessages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取历史消息失败");
      setMessages([]);
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isGeneratingResponse) return;

    // 检查是否有选中的助手
    if (!selectedAgent) {
      setError("请选择助手");
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsGeneratingResponse(true);
    setError(null);

    try {
      const jwtToken = await getJwtToken();
      if (!jwtToken) {
        throw new Error("无法获取 JWT 令牌，请先登录");
      }

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({
          prompt: userMessage.content,
          max_tokens: 1500,
          agent_id: selectedAgent.id,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("认证失败，请重新登录");
        }
        throw new Error(`请求失败: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          role: "assistant",
          content: data.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error(data.detail || "未知错误");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "发生错误");
    } finally {
      setIsGeneratingResponse(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* 消息列表区域 - 占据剩余空间 */}
      <div className="h-[560px]">
        <MessageList 
          messages={messages}
          isLoading={isGeneratingResponse}
          error={error}
        />
      </div>

      {/* 输入框区域 - 固定在底部 */}
      <div className="flex-shrink-0">
        <InputArea 
          input={input}
          isLoading={isGeneratingResponse}
          onInputChange={setInput}
          onSend={handleSend}
          onKeyPress={handleKeyPress}
        />
      </div>
    </div>
  );
}
