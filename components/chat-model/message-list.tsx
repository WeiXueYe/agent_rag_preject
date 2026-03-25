"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import { Loader2 } from "lucide-react";
import { useVirtualizer } from "@tanstack/react-virtual";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onScrollBottom?: () => void;
}

// 测量消息高度的函数
const estimateMessageSize = (message: Message): number => {
  // 基础高度：padding + margin
  const baseHeight = 16; // py-2 = 8px * 2
  const contentPadding = 24; // p-3 = 12px * 2
  
  // 估算文本高度
  // 假设每行约50个字符，行高20px
  const charsPerLine = 50;
  const lineHeight = 20;
  const lines = Math.ceil(message.content.length / charsPerLine);
  const textHeight = Math.max(lines * lineHeight, 20); // 最小20px
  
  // 总高度 = 基础高度 + 内容padding + 文本高度
  return baseHeight + contentPadding + textHeight;
};

// 消息项组件
const MessageItem = React.memo(({ message, style }: { message: Message; style?: React.CSSProperties }) => {
  if (!message) return null;

  return (
    <div style={style} className="py-2">
      <div
        className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
      >
        <div
          className={`max-w-[80%] p-3 rounded-2xl ${
            message.role === "user"
              ? "bg-black text-white rounded-br-md"
              : "bg-gray-100 text-gray-800 rounded-bl-md"
          }`}
        >
          <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        </div>
      </div>
    </div>
  );
});

// 消息列表头部组件（显示空状态）
const ListHeader = () => {
  return (
    <div className="flex items-center justify-center flex-1 text-gray-400 h-full">
      <div className="text-center">
        <p className="text-lg mb-2">开始与 AI 助手对话</p>
        <p className="text-sm">输入问题后按 Enter 发送</p>
      </div>
    </div>
  );
};

// 消息列表底部组件（显示加载状态和错误信息）
const ListFooter = ({ isLoading, error }: { isLoading: boolean; error: string | null }) => {
  return (
    <div className="py-2">
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 p-3 rounded-2xl rounded-bl-md">
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm text-gray-600">AI 正在思考...</span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="flex justify-center">
          <div className="bg-red-50 border border-red-200 px-4 py-2 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default function MessageList({ 
  messages, 
  isLoading, 
  error, 
  onScrollBottom 
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [containerHeight, setContainerHeight] = useState(500);

  // 计算容器高度
  useEffect(() => {
    const updateHeight = () => {
      if (listRef.current) {
        const height = listRef.current.clientHeight;
        setContainerHeight(height);
      }
    };

    updateHeight();
    window.addEventListener('resize', updateHeight);
    return () => window.removeEventListener('resize', updateHeight);
  }, []);

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    onScrollBottom?.();
  }, [messages, onScrollBottom]);

  // 使用 @tanstack/react-virtual 实现动态高度虚拟列表
  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => listRef.current,
    estimateSize: useCallback((index) => estimateMessageSize(messages[index]), [messages]),
    overscan: 5,
    measureElement: (element) => element.getBoundingClientRect().height,
  });

  return (
    <div 
      className="h-full overflow-y-auto" 
      ref={listRef}
      style={{
        height: '100%',
        position: 'relative',
      }}
    >
      {messages.length === 0 ? (
        <ListHeader />
      ) : (
        <div
          style={{
            height: virtualizer.getTotalSize(),
            width: '100%',
            position: 'relative',
          }}
        >
          {virtualizer.getVirtualItems().map((virtualItem) => (
            <div
              key={virtualItem.key}
              data-index={virtualItem.index}
              ref={virtualizer.measureElement}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <MessageItem message={messages[virtualItem.index]} />
            </div>
          ))}
        </div>
      )}
      
      <ListFooter isLoading={isLoading} error={error} />
      <div ref={messagesEndRef} />
    </div>
  );
}
