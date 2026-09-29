from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Session
from agent_training.database import engine, get_db
from agent_training.models import User, Conversation, Message
from agent_training.repositories.user_repository import UserRepository
from agent_training.repositories.conversation_repository import ConversationRepository
from agent_training.services.conversation_service import ConversationService
app = FastAPI()

class UserCreate(BaseModel):
    id: int
    name: str
    role: str
class ConversationCreate(BaseModel):
    user_id: int
    title: str    
class MessageCreate(BaseModel):
    conversation_id: int
    role: str
    content: str
@app.post("/conversations")
def create_conversation(
    conversation: ConversationCreate,
    session: Session = Depends(get_db),
):
    user_repo = UserRepository(session)
    conversation_repo = ConversationRepository(session)

    service = ConversationService(
        user_repo,
        conversation_repo,
    )

    try:
        db_conversation = service.create_conversation(
            conversation.user_id,
            conversation.title,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "id": db_conversation.id,
        "user_id": db_conversation.user_id,
        "title": db_conversation.title,
    }
@app.post("/messages")
def create_message(
    message: MessageCreate,
    session: Session = Depends(get_db),
):
    db_message = Message(
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
    )

    session.add(db_message)
    session.commit()

    return {
        "id": db_message.id,
        "conversation_id": db_message.conversation_id,
        "role": db_message.role,
        "content": db_message.content,
    }

@app.post("/users")
def create_user(
    user: UserCreate,
    session: Session = Depends(get_db),
):
    db_user = User(
        id=user.id,
        name=user.name,
        role=user.role,
    )

    session.add(db_user)
    session.commit()

    return {
        "id": db_user.id,
        "name": db_user.name,
        "role": db_user.role,
    }
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
