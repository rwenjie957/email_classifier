from openai import OpenAI
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    provider: str
    base_url: str
    api_key: str
    model: str
    thinking: bool


class Message:
    def __init__(self, system_prompt: str, user_content: str):
        self.messages = [
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": user_content}
        ]


@dataclass
class LLMResponse:
    content: str
    reasoning: str | None = None


class LLMProvder(ABC):
    @abstractmethod
    def chat(self, messages: Message) -> LLMResponse:
        pass


class LLMRouter:
    def __init__(self, providers: list[LLMProvder]):
        self.providers=providers
        pass

    def chat(self, m:Message):
        for provider in self.providers:
            try:
                return provider.chat(m)
            except Exception as e:
                logger.warning(f'{provider} failed: {e}')
        raise RuntimeError('all LLM failed')


class DeepSeekCompatibleProvider(LLMProvder):
    def __init__(self, config: ModelConfig):
        self.client = OpenAI(base_url=config.base_url, api_key=config.api_key)
        self.config = config
    
    def chat(self, m: Message) -> LLMResponse:
        if self.config.thinking:
            tk = "enabled"
        else:
            tk = "disabled"
        extra_body={"thinking": {"type": tk}}

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=m.messages,
            stream=False,
            extra_body=extra_body
        )
        
        if self.config.thinking:
            reasoning = response.choices[0].message.reasoning_content
        else:
            reasoning = ''
        return LLMResponse(
            content = response.choices[0].message.content,
            reasoning = reasoning
        )


class QwenProvider(LLMProvder):
    def __init__(self, config: ModelConfig):
        self.client = OpenAI(base_url=config.base_url, api_key=config.api_key)
        self.config = config
    
    def chat(self, m: Message) -> LLMResponse:
        extra_body={"enable_thinking": self.config.thinking}

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=m.messages,
            stream=False,
            extra_body=extra_body
        )
        
        if self.config.thinking:
            reasoning = response.choices[0].message.reasoning_content
        else:
            reasoning = ''
        return LLMResponse(
            content = response.choices[0].message.content,
            reasoning = reasoning
        )

# MiMo API格式与DeepSeek相同
PROVIDER_MAP = {
    "deepseek": DeepSeekCompatibleProvider,
    "mimo": DeepSeekCompatibleProvider,
    "qwen": QwenProvider
}


if __name__ == '__main__':    
    llm_service=[{
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com",
        "api_key": "",
        "model": "deepseek-v4-flash",
        "thinking": False
    },{"provider": "mimo",
        "base_url": "https://api.xiaomimimo.com/v1",
        "api_key": "",
        "model": "mimo-v2.5",
        "thinking": False}]
    model_list = []
    for i in llm_service:
        model = PROVIDER_MAP[i['provider']]
        model_list.append(model(ModelConfig(**i)))
        router = LLMRouter(model_list)

    router = LLMRouter(model_list)
    r = router.chat(Message("", ""))
    print(r.reasoning)
    print(r.content)
    pass