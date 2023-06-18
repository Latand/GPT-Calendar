import logging
from typing import Optional

from infrastructure.openai_api.base import BaseClient
from infrastructure.openai_api.types import ChatMessage, ChatCompletionResponse, ChatCompletionRequest


class OpenAIAPIClient(BaseClient):
    def __init__(self, api_key: str):
        self._api_key = api_key
        self.model = "gpt-3.5-turbo"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        base_url = "https://api.openai.com"
        super().__init__(base_url)

    async def request_chat_completion(
            self,
            messages: list[ChatMessage],
            user_id=None,
            model=None,
            temperature: float = 1,
            n: int = 1,
            max_tokens: Optional[int] = None,
            stream=False,
            functions: list = None,
    ) -> ChatCompletionResponse:
        request = ChatCompletionRequest(
            model=model or self.model,
            messages=messages,
            user=user_id,
            temperature=temperature,
            n=n,
            max_tokens=max_tokens,
            stream=stream,
            functions=functions,
        )
        status, result = await self._make_request(
            method="POST",
            url="/v1/chat/completions",
            json=request.dict(exclude_none=True),
            headers=self.headers,
        )
        logging.info(f"Chat completion response: {result}")

        return ChatCompletionResponse(**result)
