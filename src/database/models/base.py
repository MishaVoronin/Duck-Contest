from __future__ import annotations
from datetime import datetime
import uuid
import enum
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserStatusEnum(str, enum.Enum):
    USER = "user"
    CURATOR = "curator"
    ADMIN = "admin"
    BANNED = "banned"


class SolutionStatusEnum(str, enum.Enum):
    OK = "OK"
    TL = "TL"
    ML = "ML"
    CE = "CE"
    RE = "RE"


class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[UserStatusEnum | None] = mapped_column(
        String(20), nullable=True, server_default=text("'user'")
    )


class Contest(Base):
    __tablename__ = "contest"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    curator: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    is_active: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("true")
    )


class Task(Base):
    __tablename__ = "task"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    contest_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("contest.id"), nullable=True
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    task_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_file_path: Mapped[str | None] = mapped_column(String(200), nullable=True)


class Solution(Base):
    __tablename__ = "solution"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("task.id"), nullable=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[SolutionStatusEnum | None] = mapped_column(String(10), nullable=True)


class ContestAccess(Base):
    __tablename__ = "contest_access"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    contest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contest.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
