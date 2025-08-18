from datetime import datetime   
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class PriceOffer(Base):
    __tablename__ = "price_offers"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    original_price_cents: Mapped[int | None] = mapped_column(Integer())
    discounted_price_cents: Mapped[int | None] = mapped_column(Integer())
    currency: Mapped[str] = mapped_column(String(8), default="USD")

    # ✅ درست‌شده
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    game: Mapped["Game"] = relationship(back_populates="price_offers")
