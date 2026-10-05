from agent_training.repositories.user_repository import UserRepository
from agent_training.repositories.conversation_repository import ConversationRepository
from agent_training.repositories.message_repository import MessageRepository


class ConversationService:

    def __init__(
        self,
        user_repository: UserRepository,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ):
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository

    def create_conversation(
        self,
        user_id: int,
        title: str,
    ):
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        return self.conversation_repository.create(
            user_id,
            title,
        )

    def create_conversation_with_message(
        self,
        user_id: int,
        title: str,
        role: str,
        content: str,
    ):
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found")

        try:
            conversation = self.conversation_repository.create(
                user_id,
                title,
            )

            message = self.message_repository.create(
                conversation.id,
                role,
                content,
            )
            
            self.user_repository.session.commit()

            return conversation, message

        except Exception:
            self.user_repository.session.rollback()
            raise