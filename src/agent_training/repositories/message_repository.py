from sqlalchemy.orm import Session

from agent_training.models import Message


class MessageRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ):
       message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
       )
       self.session.add(message)
      

       return message

    def get_by_id(self, message_id: int):
        message = self.session.query(Message).filter(
            Message.id == message_id
        ).first()

        return message

    def get_by_conversation_id(self, conversation_id: int):
        messages = (
        self.session.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.id)
        .all()
        )
        return messages