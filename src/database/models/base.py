from __future__ import annotations
from datetime import datetime
import uuid
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Нативные PostgreSQL ENUM
UserStatusEnum = PG_ENUM(
    "user", "curator", "admin", "banned", name="user_status", create_type=True
)
SolutionStatusEnum = PG_ENUM(
    "OK", "TL", "ML", "CE", "RE", name="solution_status", create_type=True
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    mail: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str | None] = mapped_column(
        UserStatusEnum, nullable=True, server_default=text("'user'")
    )

    curated_contests: Mapped[list["Contest"]] = relationship(
        "Contest", back_populates="curator_user", foreign_keys="[Contest.curator]"
    )
    solutions: Mapped[list["Solution"]] = relationship(
        "Solution", back_populates="user"
    )
    contest_accesses: Mapped[list["ContestAccess"]] = relationship(
        "ContestAccess", back_populates="user"
    )


class Contest(Base):
    __tablename__ = "contest"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    curator: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("true")
    )

    curator_user: Mapped[User] = relationship("User", back_populates="curated_contests")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="contest")
    access_records: Mapped[list["ContestAccess"]] = relationship(
        "ContestAccess", back_populates="contest"
    )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    contest_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("contest.id"), nullable=True
    )
    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    task_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_file_path: Mapped[str | None] = mapped_column(String(200), nullable=True)

    contest: Mapped[Contest] = relationship("Contest", back_populates="tasks")
    solutions: Mapped[list["Solution"]] = relationship(
        "Solution", back_populates="task"
    )


class Solution(Base):
    __tablename__ = "solution"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("task.id"), nullable=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        "datetime", DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[str | None] = mapped_column(SolutionStatusEnum, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="solutions")
    task: Mapped[Task] = relationship("Task", back_populates="solutions")


class ContestAccess(Base):
    __tablename__ = "contest_access"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    contest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contest.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    contest: Mapped[Contest] = relationship("Contest", back_populates="access_records")
    user: Mapped[User] = relationship("User", back_populates="contest_accesses")
