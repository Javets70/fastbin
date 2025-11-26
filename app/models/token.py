import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import override

from app.core.database import Base


class Token(Base):
    __tablename__: str = "tokens"

    jti: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    token_type: Mapped[str] = mapped_column(String(30), nullable=False)

    # If token_type == "access" then paired_jti refers to "refresh"
    # otherwise , paired_jti refers to "access"
    paired_jti: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    is_blacklisted: Mapped[bool] = mapped_column(Boolean, server_default="FALSE")
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    blacklist_reason: Mapped[str] = mapped_column(String(300), nullable=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    _metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, server_default="{}")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tokens")

    @override
    def __repr__(self):
        return f"<Token(JTI={self.jti}, \npaired_jti={self.paired_jti}, \nuser={self.user if self.user else 'Anon'})>"
