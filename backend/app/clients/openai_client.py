from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key)

    def chat(self, messages: list[dict], model: str, **kwargs) -> str:
        response = self.client.responses.create(
            model=model,
            input=messages,
            **kwargs
        )
        return response.output_text