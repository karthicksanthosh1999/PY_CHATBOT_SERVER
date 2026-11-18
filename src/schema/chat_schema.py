from datetime import datetime
from pydantic import Field, BaseModel, ConfigDict

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    question: str = Field(
        min_length=1,
        max_length=5000
    )

class ChatResponse(BaseModel):
    conversation_id: int
    answer: str

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpdateConversationRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
        description="new conversation title"
    )