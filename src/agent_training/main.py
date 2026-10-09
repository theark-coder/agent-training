from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Session
from agent_training.database import engine, get_db
from agent_training.models import User, Conversation, Message
from agent_training.repositories.user_repository import UserRepository
from agent_training.repositories.conversation_repository import ConversationRepository
from agent_training.services.conversation_service import ConversationService
from agent_training.repositories.message_repository import MessageRepository

from typing import Literal


from sqlalchemy.exc import IntegrityError

from agent_training.schemas import (
    UserCreate,
    UserResponse,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
app = FastAPI()
@app.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=201,
)
def create_conversation(
    conversation: ConversationCreate,
    session: Session = Depends(get_db),
):
    service = ConversationService(
        UserRepository(session),
        ConversationRepository(session),
        MessageRepository(session),
    )

    try:
        db_conversation, db_message = (
            service.create_conversation_with_message(
                conversation.user_id,
                conversation.title,
                "user",
                "这是事务测试消息",
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "conversation_id": db_conversation.id,
        "message_id": db_message.id,
        "title": db_conversation.title,
        "message": db_message.content,
    }

@app.post(
    "/messages",
    response_model=MessageResponse,
    status_code=201,
)
def create_message(
    message: MessageCreate,
    session: Session = Depends(get_db),
):
    conversation = session.get(
        Conversation,
        message.conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db_message = Message(
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
    )

    try:
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
    except Exception:
        session.rollback()
        raise

    return db_message

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_db),
):
    db_user = User(
        id=user.id,
        name=user.name,
        role=user.role,
    )

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="User ID already exists",
        ) from exc

    return db_user
@app.get("/hello")
def hello(name: str = Query(min_length=2)):
    return {"message": f"Hello, {name}!"}
@app.put("/db/users/{user_id}")
def update_user(
    user_id: int,
    session: Session = Depends(get_db),
):

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "AI Engineer"
    session.commit()
    return {
    "id": user.id,
    "name": user.name,
    "role": user.role,
}
@app.get("/db/users/{user_id}")
def get_db_user(user_id: int, session: Session = Depends(get_db)):
   

    user = session.query(User).filter(User.id == user_id).first()

    

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
@app.delete("/db/users/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_db),
):

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {
    "message": "User deleted successfully"
    }
@app.post("/conversations/with-message")
def create_conversation_with_message(
    conversation: ConversationCreate,
    session: Session = Depends(get_db),
):
    user_repo = UserRepository(session)
    conversation_repo = ConversationRepository(session)
    message_repo = MessageRepository(session)

    service = ConversationService(
        user_repo,
        conversation_repo,
        message_repo,
    )

    try:
        db_conversation = service.create_conversation(
            conversation.user_id,
            conversation.title,
        )
        session.commit()
    except ValueError as exc:
        session.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except Exception:
        session.rollback()
        raise
    return {
        "conversation_id": db_conversation.id,
        "message_id": db_message.id,
        "title": db_conversation.title,
        "message": db_message.content,
    }