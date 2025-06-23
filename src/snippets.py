model_list = [
    "deepseek-chat",
    "deepseek-reasoner",
    "doubao-1-5-lite-32k-250115",
    "doubao-1-5-thinking-pro-250415",
    "gemini-2.5-flash-preview-05-20",
    "glm-z1-flash",
    "glm-z1-air",
    "qwen-max-0125",
    "hunyuan-t1-latest",
    "x1"
]

model_to_key_name = {
    "deepseek-chat": "DEEPSEEK_API_KEY",
    "deepseek-reasoner": "DEEPSEEK_API_KEY",
    "doubao-1-5-lite-32k-250115": "DOUBAO_API_KEY",
    "doubao-1-5-thinking-pro-250415": "DOUBAO_API_KEY",
    "gemini-2.5-flash-preview-05-20": "GEMINI_API_KEY",
    "glm-z1-flash": "ZHIPU_API_KEY",
    "glm-z1-air": "ZHIPU_API_KEY",
    "qwen-max-0125": "DASHSCOPE_API_KEY",
    "hunyuan-t1-latest": "HUNYUAN_API_KEY",
    "x1": "SPARK_API_KEY"
}

model_to_url = {
    "deepseek-chat": "https://api.deepseek.com",
    "deepseek-reasoner": "https://api.deepseek.com",
    "doubao-1-5-lite-32k-250115": "https://ark.cn-beijing.volces.com/api/v3",
    "doubao-1-5-thinking-pro-250415": "https://ark.cn-beijing.volces.com/api/v3",
    "glm-z1-flash": "https://open.bigmodel.cn/api/paas/v4/",
    "glm-z1-air": "https://open.bigmodel.cn/api/paas/v4/",
    "qwen-max-0125": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "hunyuan-t1-latest": "https://api.hunyuan.cloud.tencent.com/v1",
    "x1": "https://spark-api-open.xf-yun.com/v2"
}

model_to_API = {
    "deepseek-chat": "OpenAI",
    "deepseek-reasoner": "OpenAI",
    "doubao-1-5-lite-32k-250115": "OpenAI",
    "doubao-1-5-thinking-pro-250415": "OpenAI",
    "gemini-2.5-flash-preview-05-20": "Google",
    "glm-z1-flash": "OpenAI",
    "glm-z1-air": "OpenAI",
    "qwen-max-0125": "OpenAI",
    "hunyuan-t1-latest": "OpenAI",
    "x1": "OpenAI"
}

class InvalidAction(Exception):
    def __init__(self, *args):
        super().__init__(args)

class LLMError(Exception):
    def __init__(self, *args):
        super().__init__(args)

class LLMRateLimitError(LLMError):
    def __init__(self, *args):
        super().__init__(args)