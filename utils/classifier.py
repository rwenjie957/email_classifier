from openai import OpenAI
import logging

logger = logging.getLogger(__name__)
class LLM:
    def __init__(self, config: dict):
        self.provider = config["provider"]
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.thinking = config["thinking"]
        

    def classify(self, system_prompt, user_content):
        self.messages = [
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": user_content}
        ]
        if self.provider == 'deepseek':
            return self.deepseek()
        else:
            logger.error("暂不支持其它厂商API， 请等待后续更新")
        
    def deepseek(self):
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        if self.thinking:
            tk = "enabled"
        else:
            tk = "disabled"
        
        extra_body={"thinking": {"type": tk}}

        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=False,
            extra_body=extra_body
        )

        reason = ''
        if self.thinking:
            reason = response.choices[0].message.reasoning_content
        result = response.choices[0].message.content

        return reason, result

if __name__ == '__main__':
    pass