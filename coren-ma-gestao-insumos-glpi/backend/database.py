"""Conexão SQLite e dependência de sessão SQLAlchemy."""
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent / "estoque.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def configurar_sqlite(connection: object, _: object) -> None:
    """Ativa integridade referencial e espera curta para locks de escrita."""
    cursor = connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base dos modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Abre uma sessão de banco por requisição e sempre a fecha."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
