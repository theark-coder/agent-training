from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session

from agent_training.config import get_settings

settings = get_settings()

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.mysql_user,
    password=settings.mysql_password,
    host=settings.mysql_host,
    port=settings.mysql_port,
    database=settings.mysql_database,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def check_database() -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def get_db():
    with Session(engine) as session:
        yield session