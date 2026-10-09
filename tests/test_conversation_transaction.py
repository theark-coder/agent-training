import pytest

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session

from agent_training.models import Base, User, Conversation, Message
from agent_training.repositories.user_repository import UserRepository
from agent_training.repositories.conversation_repository import (
    ConversationRepository,
)
from agent_training.repositories.message_repository import MessageRepository
from agent_training.services.conversation_service import ConversationService


@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'transaction_test.db'}"
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(User(id=1, name="test", role="student"))
        session.commit()
        yield session

    engine.dispose()


def make_service(session):
    return ConversationService(
        UserRepository(session),
        ConversationRepository(session),
        MessageRepository(session),
    )


def count_rows(session, model):
    return session.scalar(
        select(func.count()).select_from(model)
    )


def test_transaction_success(db_session):
    service = make_service(db_session)

    conversation, message = (
        service.create_conversation_with_message(
            1,
            "事务成功测试",
            "user",
            "Hello Agent",
        )
    )

    assert conversation.id is not None
    assert message.id is not None

    # 新 Session 验证数据已经提交
    with Session(db_session.bind) as verify_session:
        assert count_rows(verify_session, Conversation) == 1
        assert count_rows(verify_session, Message) == 1


def test_transaction_rollback(db_session):
    service = make_service(db_session)

    # 模拟 Message INSERT 执行时数据库出错
    def fail_message_insert(mapper, connection, target):
        raise RuntimeError("Simulated message insert failure")

    event.listen(Message, "before_insert", fail_message_insert)

    try:
        with pytest.raises(
            RuntimeError,
            match="Simulated message insert failure",
        ):
            service.create_conversation_with_message(
                1,
                "事务失败测试",
                "user",
                "Hello Agent",
            )
    finally:
        event.remove(
            Message,
            "before_insert",
            fail_message_insert,
        )

    # 使用新 Session 验证失败的事务没有留下数据
    with Session(db_session.bind) as verify_session:
        assert count_rows(verify_session, Conversation) == 0
        assert count_rows(verify_session, Message) == 0