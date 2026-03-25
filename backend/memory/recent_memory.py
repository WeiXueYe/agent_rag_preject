import uuid
import redis
import json




class RecentMemory:
    """
    Redis Memory 管理类
    用于：
    - recent 对话
    - task memory
    """

    def __init__(self,
                 user_id: uuid.UUID,
                 agent_id: int,
                 host="localhost", 
                 port=6379, 
                 db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.user_id = user_id
        self.agent_id = agent_id

    def get_recent(self, n=30):
        """
        获取最近 n 条对话
        """
        key = f"chat:{self.user_id}:{self.agent_id}"
        messages = self.r.lrange(key, -n, -1)
        return "\n".join(messages)
    
    def get_list_recent(self, n=30):
        """
        获取最近 n 条对话（列表格式）
        """
        key = f"chat:{self.user_id}:{self.agent_id}"
        messages = self.r.lrange(key, -n, -1)
        print(type(messages))
        return [json.loads(msg) for msg in messages]
    
    def turn2json(self, message: str, role: str):
        """
        将字符串转换为 JSON 格式
        """
        try:
            # 将字典转换为 JSON 字符串
            return json.dumps(
                {"role": role, "content": message},
                ensure_ascii=False
            )
        except json.JSONDecodeError:
            return None

    def save_message(self,user_message: str, ai_message: str, max_len=20):
        """
        保存对话（自动裁剪长度）
        用户消息,ai消息,最大长度
        """
        key = f"chat:{self.user_id}:{self.agent_id}"
        # 保存消息
        self.r.rpush(key, self.turn2json(user_message, "user"))
        self.r.rpush(key, self.turn2json(ai_message, "ai"))
        # 只保留最近 N 条
        self.r.ltrim(key, -max_len, -1)