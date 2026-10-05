from sqlalchemy.orm import Session

from agent_training.models import Conversation


class ConversationRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, title: str):
        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.session.add(conversation)
        self.session.flush()

        return conversation

    def get_by_id(self, conversation_id: int):
        conversation = self.session.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        return conversation

    def get_by_user_id(self, user_id: int):
        conversations = self.session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()

        return conversations