import os
import json

from dotenv import load_dotenv
from groq import Groq
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.database.models import Conversation, Message

load_dotenv()

class ChatService:
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME")
        
        if not api_key:
            raise RuntimeError("API key is not found")
        if not self.model_name:
            raise RuntimeError("Model name is not found")

        self.client = Groq(
            api_key=api_key
        )

    def chat_stream( self, db: Session, question: str, conversation_id: int | None = None, user_id: int = None ):
    
    # 1. Create or fetch conversation
    
        if conversation_id is None:
            conversation = Conversation(
            title=question[:200],
            user_id=user_id
            )
            db.add(conversation)
            db.flush()

        else:
            conversation_statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )

            conversation = db.scalar(conversation_statement)

            if conversation is None:
                raise ValueError("Conversation Not Found")

    # 2. Fetch previous messages
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at, Message.id)
        )

        previous_messages = db.scalars(statement).all()

        # 3. Prepare LLM messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI teacher."
            }
        ]

        for previous_message in previous_messages:
            messages.append({
                "role": previous_message.role,
                "content": previous_message.content
            })

        messages.append({
            "role": "user",
            "content": question
        })

        # 4. Save user message
        db.add(
            Message(
                conversation_id=conversation.id,
                role="user",
                content=question
            )
        )
        db.commit()

        # 5. Send conversation ID
        yield (
            "event: conversation\n"
            f"data: {json.dumps({'conversation_id': conversation.id})}\n\n"
        )

        full_answer = ""

        try:
            # 6. Start Groq streaming
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                stream=True
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content

                if content:
                    full_answer += content

                    yield ( "event: token\n" f"data: {json.dumps({'content': content})}\n\n")

            # 7. Save complete assistant response
            db.add(
                Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=full_answer
                )
            )
            db.commit()

            yield "event: done\ndata: {}\n\n"

        except Exception as error:
            db.rollback()

            yield (
                "event: error\n"
                f"data: {json.dumps({'message': str(error)})}\n\n"
            )


    def chat(self, db:Session, user_id: int, question: str, conversation_id: int | None = None):

        if conversation_id is None:
            conversation = Conversation(
                title = question[:200],
                user_id=user_id   
            )
            db.add(conversation)
            db.flush()
        else:
            conversation = db.get(Conversation, conversation_id)

            if conversation is None:
                raise ValueError("Conversation Not Found")

        statement = select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at, Message.id)
        previous_message = db.scalars(statement).all()

        messages = [
            {
                "role" : "system",
                "content" : "You are a helpful AI teacher."
            }
        ]

        for message in previous_message:
            messages.append({
                "role" : message.role,
                "content" : message.content
            })

        messages.append({
            "role" : "user",
            "content" : question
        })

        response = self.client.chat.completions.create(
            model = self.model_name,
            temperature=0.3,
            max_tokens=500,
            messages=messages
        )

        answer = response.choices[0].message.content or ""

        db.add_all([
            Message(
                conversation_id = conversation.id,
                role="user",
                content=question
            ),
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer
            )
        ])

        db.commit()

        return conversation.id, answer

    def get_conversations(self, db: Session, user_id: int):
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )

        conversations = db.scalars(statement).all()

        return conversations

    def get_messages(self, db: Session, conversation_id: int, user_id: int):
        conversation = db.get(Conversation, conversation_id)

        if conversation is None:
            raise ValueError("Conversation Not Found")

        statement = (
            select(Message).join(Conversation).where(Message.conversation_id == conversation_id, Conversation.user_id == user_id).order_by(Message.created_at.asc(), Message.id)
        )

        messages = db.scalars(statement).all()

        return messages

    def update_conversation(self, db: Session, conversation_id: int, title: str):
        conversation = db.get(Conversation, conversation_id)

        if conversation is None:
            raise ValueError("Conversation Not Found")

        conversation.title = title

        db.commit()
        db.refresh(conversation)

        return conversation

    def delete_conversation(self, db: Session, conversation_id: int, user_id: int):

        statement = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        conversation = db.scalar(statement)

        if conversation is None:
            raise ValueError("Conversation Not Found")

        db.delete(conversation)
        db.commit()

        return {
            "message" : "Conversation Deleted Successfully"
        }
