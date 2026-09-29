from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi import Query
from sqlalchemy.orm import Session
from agent_training.database import engine, get_db
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
@app.put("/db/users/{user_id}")
def update_user(user_id: int):
    session = Session(engine)

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
def delete_user(user_id: int):
    session = Session(engine)

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {
    "message": "User deleted successfully"
    }
