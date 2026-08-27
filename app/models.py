from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0)
