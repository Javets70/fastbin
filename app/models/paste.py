from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing_extensions import override
from app.core.database import Base


class Paste(Base):
    __tablename__: str = "pastes"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Paste Content
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(
        String(50), default="plaintext", nullable=True
    )

    # URL & Access
    short_url: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Expiration
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Foreign Key
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

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
    user: Mapped["User"] = relationship("User", back_populates="pastes")

    # Composite Indexes for performance
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_expires_public", "expires_at", "is_public"),
    )

    @override
    def __repr__(self):
        return f"<Paste(id={self.id}, short_url={self.short_url}, title={self.title})>"
