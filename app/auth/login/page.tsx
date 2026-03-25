import { LoginForm } from "@/components/login-form";
import { CheckSquareOutlined } from '@ant-design/icons';



export default function Page() {
  return (
    <div className="flex min-h-svh w-full bg-white">
      {/* 左侧介绍区域 */}
      <div className="w-2/3 p-12 flex flex-col justify-center bg-black text-white">
        <div className="max-w-xl">
          <h1 className="text-4xl font-bold mb-6">Agent RAG</h1>
          <p className="text-xl mb-4">
            智能代理 + 检索增强生成技术，打造新一代 AI 应用
          </p>
          <p className="mb-4">
            <CheckSquareOutlined /> &nbsp; 基于最新的大语言模型 <br />
            <CheckSquareOutlined /> &nbsp; 高效的知识库检索系统<br />
            <CheckSquareOutlined /> &nbsp; 智能代理自动处理复杂任务<br />
            <CheckSquareOutlined /> &nbsp; 实时数据更新与分析
          </p>
          <p className="mb-4">
            <CheckSquareOutlined /> &nbsp; 多模态内容理解<br />
            <CheckSquareOutlined /> &nbsp; 个性化推荐算法<br />
            <CheckSquareOutlined /> &nbsp; 安全可靠的用户认证<br />
            <CheckSquareOutlined /> &nbsp; 可扩展的系统架构
          </p>
          <div className="my-8 border-t border-gray-600"></div>
          <p className="text-gray-300">
            登录系统，开始体验智能时代的工作方式
          </p>
        </div>
      </div>
      
      {/* 右侧登录区域 */}
      <div className="w-1/3 p-8 flex items-center justify-center">
        <div className="w-full max-w-md">
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
