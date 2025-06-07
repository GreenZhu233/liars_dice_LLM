from openai import OpenAI
import json

class OpenAILLMClient:
    def __init__(self, model="deepseek-chat"):
        """初始化LLM客户端"""
        # 打开并读取文件
        with open('config/keys.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        match model:
            case "deepseek-chat":
                api_key = config.get("DEEPSEEK_API_KEY")
                base_url = "https://api.deepseek.com"
            case "deepseek-reasoner":
                api_key = config.get("DEEPSEEK_API_KEY")
                base_url = "https://api.deepseek.com"
            case "doubao":
                api_key = config.get("DOUBAO_API_KEY")
                base_url = "https://ark.cn-beijing.volces.com/api/v3"
            case _:
                raise ValueError("Unsupported LLM provider in configuration")

        self.model = model

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
    def chat(self, messages):
        """与LLM交互
        
        Args:
            messages: 消息列表
        
        Returns:
            tuple: (content, reasoning_content)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={'type': 'json_object'}
            )
            if response.choices:
                message = response.choices[0].message
                content = message.content if message.content else ""
                reasoning_content = getattr(message, "reasoning_content", "")
                print(f"LLM推理内容: {content}")
                return content, reasoning_content
            
            return "", ""
                
        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            return "", ""