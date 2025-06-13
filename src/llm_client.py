from openai import OpenAI
from google import genai
import json
from src.snippets import *
from pydantic import BaseModel

class OpenAILLMClient:
    def __init__(self, model="deepseek-chat"):
        """初始化LLM客户端"""
        # 打开并读取文件
        with open('config/keys.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        try:
            api_key = config.get(model_to_key_name[model])
            base_url = model_to_url[model]
        except:
            raise ValueError("不支持的LLM供应商！")

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
                return content, reasoning_content
            
            return "", ""
                
        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            return "", ""

class Answer(BaseModel):
    """LLM返回的JSON格式"""
    recipe_name: str
    challenge: bool
    value: int
    number: int
    reason: str
    behaviour: str

class GoogleLLMClient:
    def __init__(self, model="gemini-2.0-flash"):
        """初始化LLM客户端"""
        # 打开并读取文件
        with open('config/keys.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        try:
            api_key = config.get(model_to_key_name[model])
        except:
            raise ValueError("不支持的LLM供应商！")

        self.model = model

        self.client = genai.Client(
            api_key=api_key
        )

    def chat(self, messages):
        """与LLM交互
        
        Args:
            messages: 消息列表
        
        Returns:
            tuple: (content, reasoning_content)
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[Answer],
                }
            )
            if content := response.text:
                reasoning_content = ""
                return content, reasoning_content
            
            return "", ""
                
        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            return "", ""