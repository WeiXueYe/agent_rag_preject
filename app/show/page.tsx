import { OuterFrameContainer, OuterFrameItem } from "@/components/frame/outer-frame";
import ChatDemo from "./chat-demo";

export default function Page() {
  return (
    <div className="h-full">
      <OuterFrameContainer>
        <OuterFrameItem>
          <h3 className="font-bold mb-2">API 调用演示</h3>
          <p className="text-sm text-gray-600 mb-4">
            这个演示展示了如何从 Next.js 前端调用 FastAPI 后端接口
          </p>
          <div className="space-y-2 text-sm">
            <div className="p-2 bg-gray-50 rounded">
              <strong>后端：</strong>FastAPI (Python)
            </div>
            <div className="p-2 bg-gray-50 rounded">
              <strong>接口：</strong>POST /chat
            </div>
            <div className="p-2 bg-gray-50 rounded">
              <strong>端口：</strong>8000
            </div>
            <div className="p-2 bg-gray-50 rounded">
              <strong>模型：</strong>通义千问 (Qwen-Plus)
            </div>
          </div>
        </OuterFrameItem>

        <OuterFrameItem>
          <h3 className="font-bold mb-2">技术架构</h3>
          <div className="space-y-3 text-sm">
            <div>
              <strong className="block mb-1">前端 → 后端</strong>
              <p className="text-gray-600">
                Next.js 使用 fetch API 发送 HTTP 请求到 FastAPI 服务器
              </p>
            </div>
            <div>
              <strong className="block mb-1">后端 → AI 模型</strong>
              <p className="text-gray-600">
                FastAPI 调用 DashScope API 与通义千问模型交互
              </p>
            </div>
            <div>
              <strong className="block mb-1">数据流</strong>
              <p className="text-gray-600">
                用户输入 → 前端处理 → 后端 API → AI 模型 → 返回结果 → 前端显示
              </p>
            </div>
          </div>
        </OuterFrameItem>

        <OuterFrameItem>
          <h3 className="font-bold mb-2">实时对话</h3>
          <ChatDemo />
        </OuterFrameItem>
      </OuterFrameContainer>
    </div>
  );
}