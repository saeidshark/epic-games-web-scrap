from datetime import date
from sqlalchemy import String, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    release_date: Mapped[date | None] = mapped_column(Date(), nullable=True)

    publisher_id: Mapped[int | None] = mapped_column(ForeignKey("publishers.id", ondelete="SET NULL"))
    developer_id: Mapped[int | None] = mapped_column(ForeignKey("developers.id", ondelete="SET NULL"))

    publisher: Mapped["Publisher | None"] = relationship(back_populates="games")
    developer: Mapped["Developer | None"] = relationship(back_populates="games")

    price_offers: Mapped[list["PriceOffer"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    genres: Mapped[list["GameGenre"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    platforms: Mapped[list["GamePlatform"]] = relationship(back_populates="game", cascade="all, delete-orphan")
