from typing import List, Optional

from pydantic import BaseModel, Field


class FunctionCall(BaseModel):
    name: str
    arguments: str = None


class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = Field(None)
    name: Optional[str] = Field(None)
    function_call: Optional[FunctionCall] = Field(None)


class Choice(BaseModel):
    index: int
    message: ChatMessage


class Conversation:
    def __init__(self, messages: List[ChatMessage] = None):
        self.messages = messages or []

    def add_system_message(self, content: str, name: str = None):
        if len(self.messages) > 1:
            self.messages[0] = ChatMessage(role="system", content=content, name=name)
        else:
            self.messages.append(ChatMessage(role="system", content=content, name=name))

    def add_user_message(self, content: str, name: str = None):
        self.messages.append(ChatMessage(role="user", content=content, name=name))

    def add_assistant_message(self, content: str, name: str = None):
        self.messages.append(ChatMessage(role="assistant", content=content, name=name))

    def add_function_output(self, content: str, function_name: str):
        self.messages.append(
            ChatMessage(role="function", content=content, name=function_name)
        )

    @classmethod
    def from_raw(cls, history: List[dict] = None):
        if history is None:
            history = []

        messages = [ChatMessage.parse_raw(m) for m in history]
        return cls(messages=messages)

    def to_raw(self):
        return [m.json(exclude_none=True) for m in self.messages]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: float = 1
    top_p: float = 1
    user: str = None
    stream: bool = False
    max_tokens: Optional[int] = None
    n: int = 1
    functions: list = None
    function_call = "auto"


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int = None
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    choices: List[Choice]
    usage: Usage
