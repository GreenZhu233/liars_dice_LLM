model_list = [
    "deepseek-chat",
    "deepseek-reasoner",
    "doubao-1-5-lite-32k-250115",
    "doubao-1-5-thinking-pro-250415",
    "gemini-2.5-flash-preview-05-20"
]

model_to_key_name = {
    "deepseek-chat": "DEEPSEEK_API_KEY",
    "deepseek-reasoner": "DEEPSEEK_API_KEY",
    "doubao-1-5-lite-32k-250115": "DOUBAO_API_KEY",
    "doubao-1-5-thinking-pro-250415": "DOUBAO_API_KEY",
    "gemini-2.5-flash-preview-05-20": "GOOGLE_API_KEY"
}

model_to_url = {
    "deepseek-chat": "https://api.deepseek.com",
    "deepseek-reasoner": "https://api.deepseek.com",
    "doubao-1-5-lite-32k-250115": "https://ark.cn-beijing.volces.com/api/v3",
    "doubao-1-5-thinking-pro-250415": "https://ark.cn-beijing.volces.com/api/v3"
}

model_to_API = {
    "deepseek-chat": "OpenAI",
    "deepseek-reasoner": "OpenAI",
    "doubao-1-5-lite-32k-250115": "OpenAI",
    "doubao-1-5-thinking-pro-250415": "OpenAI",
    "gemini-2.5-flash-preview-05-20": "Google"
}