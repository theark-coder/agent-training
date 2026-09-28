from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Session
from agent_training.database import engine
from agent_training.models import User
app = FastAPI()

class UserCreate(BaseModel):
    id: int
    name: str
    role: str
@app.post("/users")
def create_user(user: UserCreate):
    db_user = User(
        id=user.id,
        name=user.name,
        role=user.role,
    )
    session = Session(engine)
    session.add(db_user)
    session.commit()
   
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
    }


@app.get("/hello")
def hello(name: str = Query(min_length=2)):
    return {"message": f"Hello, {name}!"}
@app.get("/db/users/{user_id}")
def get_db_user(user_id: int):
    session = Session(engine)

    user = session.query(User).filter(User.id == user_id).first()

    session.close()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
