from openai import OpenAI
from google import genai
import json
from src.snippets import *
from pydantic import BaseModel, create_model, Field

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

    def reflect(self, messages, *args):
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

class Action(BaseModel):
    """LLM决策输出的JSON格式"""
    challenge: bool
    value: int
    number: int
    reason: str
    behaviour: str

class GoogleLLMClient:
    def __init__(self, model="gemini-2.5-flash-preview-05-20"):
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
                contents=messages[0]['content'] + messages[1]['content'],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Action,
                }
            )
            if content := response.text:
                reasoning_content = ""
                return content, reasoning_content

            return "", ""

        except Exception as e:
            print(f"LLM调用出错: {str(e)}")
            return "", ""

    def reflect(self, messages, other_players):

        # 配置LLM反思的json输出格式
        response_format = {p.name: (str, Field(description="填入中文字符串")) for p in other_players}
        response_schema = create_model("ReflectResponse", **response_format)

        response = self.client.models.generate_content(
            model=self.model,
            contents=messages[0]['content'] + messages[1]['content'],
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            }
        )
        if content := response.text:
            reasoning_content = ""
            return content, reasoning_content

        return "", ""