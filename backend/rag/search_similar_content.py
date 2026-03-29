from supabase import Client


def search_similar_content(query_vector, agent_id, supabase):
    try:
        # 1. 调用 RPC 获取原始数据
        # 建议 match_threshold 设为 0.5 左右，防止无关内容干扰 AI
        response = supabase.rpc('match_rag_contents', {
            'query_embedding': query_vector,
            'match_threshold': 0.3,              # 相似度阈值
            'match_count': 3,                   # 返回最相关的 3 条
            'target_agent_id': int(agent_id)
        }).execute()

        # 2. 提取并格式化内容
        if not response.data or len(response.data) == 0:
            return "未找到相关的本地知识库内容。"

        # 将多条内容拼接，并加上编号标签，方便 AI 理解
        formatted_parts = []
        for i, item in enumerate(response.data):
            content_snippet = item.get('content', '').strip()
            if content_snippet:
                formatted_parts.append(f"[相关知识片段 {i+1}]:\n{content_snippet}")
                print(f"[相关知识片段 {i+1}]:\n{content_snippet}")

        # 用换行符连接所有片段
        return "\n\n".join(formatted_parts)

    except Exception as e:
        print(f"向量搜索发生错误: {e}")
        return "知识库搜索暂时不可用。"	