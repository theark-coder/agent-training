from agent_training.repositories.user_repository import UserRepository
from agent_training.repositories.conversation_repository import ConversationRepository


class ConversationService:

    def __init__(
        self,
        user_repository: UserRepository,
        conversation_repository: ConversationRepository,
    ):
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository

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