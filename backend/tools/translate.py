import json
import os
from langchain.tools import tool
from tencentcloud.common import credential
from tencentcloud.tmt.v20180321 import tmt_client, models
from dotenv import load_dotenv


# LangChain 会自动解析你的函数签名
@tool
def tencent_translate(text: str) -> str:
    """
    腾讯云通用翻译函数，用于处理文本翻译请求，该工具会自动识别语言并将其翻译成中文
    用户可能会输入中外混杂的内容，你需要将其中的外语内容翻译成中文
    :param text: 待翻译的文本,用户输入的文本中的外语内容
    :return: 翻译后的文本内容
    """
    load_dotenv()

    source = "auto"
    target = "zh"
    # --- 替换为你自己的腾讯云密钥 ---
    SECRET_ID = os.getenv("SECRET_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")
    REGION = "ap-guangzhou" # 地域，通常广州或上海即可

    print("使用腾讯云翻译服务")

    try:
        # 1. 认证信息
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        client = tmt_client.TmtClient(cred, REGION)

        # 2. 构造请求对象
        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": source,
            "Target": target,
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))

        # 3. 发送请求并获取响应
        resp = client.TextTranslate(req)
        
        # 4. 提取结果
        result = json.loads(resp.to_json_string())
        return result.get("TargetText", "翻译失败，未获取到结果")

    except Exception as e:
        return f"翻译出错: {str(e)}"
    
