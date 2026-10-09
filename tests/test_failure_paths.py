import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from agent_training.models import Base, User, Conversation
from agent_training.schemas import MessageCreate
from agent_training.repositories.user_repository import UserRepository
from agent_training.repositories.conversation_repository import (
    ConversationRepository,
)
from agent_training.repositories.message_repository import (
    MessageRepository,
)
from agent_training.services.conversation_service import (
    ConversationService,
)


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'failure_test.db'}"
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


def test_nonexistent_user(db_session):
    """不存在的用户不能创建会话。"""

    service = ConversationService(
        UserRepository(db_session),
        ConversationRepository(db_session),
        MessageRepository(db_session),
    )

    with pytest.raises(ValueError, match="User not found"):
        service.create_conversation_with_message(
            999999,
            "不存在的用户",
            "user",
            "Hello",
        )

    with Session(db_session.bind) as verify_session:
        count = verify_session.scalar(
            select(func.count()).select_from(Conversation)
        )
        assert count == 0


@pytest.mark.parametrize(
    "payload",
    [
        {
            "conversation_id": 1,
            "role": "admin",
            "content": "Hello",
        },
        {
            "conversation_id": 1,
            "role": "user",
            "content": "",
        },
        {
            "conversation_id": "abc",
            "role": "user",
            "content": "Hello",
        },
    ],
)
def test_invalid_message(payload):
    """非法消息应在进入业务层之前被拒绝。"""

    with pytest.raises(ValidationError):
        MessageCreate.model_validate(payload)