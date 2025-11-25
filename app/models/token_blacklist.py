from datetime import datetime
import uuid
from typing_extensions import override

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class BlacklistedToken(Base):
    __tablename__: str = "blacklisted_token"

    jti: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    access_token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # user: Mapped["User"] = relationship("BlacklistedToken", back_populates="token")
    @override
    def __repr__(self):
        return f"<BlacklistedToken(token_id={self.jti}, \naccess_token={self.access_token}, \nrefresh_token={self.refresh_token})>"
