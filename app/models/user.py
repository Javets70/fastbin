from typing_extensions import override
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # User Information
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    pastes: Mapped[list["Paste"]] = relationship(
        "Paste", back_populates="user", cascade="all, delete-orphan"
    )

    @override
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
