from sqlalchemy.orm import Session

from agent_training.models import User


class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int):
        user = self.session.query(User).filter(User.id == user_id).first()
        return user

    def create(self, name: str, role: str):
        db_user = User(
            name=name,
            role=role,
        )

        self.session.add(db_user)
        self.session.commit()

        return db_user