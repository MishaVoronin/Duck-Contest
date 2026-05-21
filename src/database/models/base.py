from __future__ import annotations
from datetime import datetime
import uuid
import enum
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserStatusEnum(str, enum.Enum):
    USER = "user"
    CURATOR = "curator"
    MODERATOR = "moderator"
    BANNED = "banned"


class SolutionStatusEnum(str, enum.Enum):
    OK = "OK"
    TL = "TL"
    ML = "ML"
    CE = "CE"
    RE = "RE"
    WA = "WA"


# class AnswerTypeEnum(str, enum.Enum):
#    ONLI_ANSWER = "ONLI_ANSWER"


class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[UserStatusEnum] = mapped_column(
        String(20), nullable=False, server_default=text("'user'")
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    token = mapped_column(String, unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_revoked = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at = mapped_column(DateTime(timezone=True), nullable=True)


class Contest(Base):
    __tablename__ = "contest"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    curator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_ended: Mapped[bool] = mapped_column(default=True, server_default="False")
    is_active: Mapped[bool] = mapped_column(default=True, server_default="False")
    is_public: Mapped[bool] = mapped_column(default=True, server_default="False")


class Task(Base):
    __tablename__ = "task"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    contest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contest.id"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)
    points: Mapped[int] = mapped_column(Integer)
    # test: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    # answer_type:Mapped[AnswerTypeEnum] = mapped_column(String(255), nullable=False)


class Solution(Base):
    __tablename__ = "solution"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("task.id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[SolutionStatusEnum] = mapped_column(String(10), nullable=False)
    points: Mapped[int] = mapped_column(Integer)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)


class ContestAccess(Base):
    __tablename__ = "contest_access"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    contest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contest.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
