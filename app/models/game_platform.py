from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class GamePlatform(Base):
    __tablename__ = "game_platforms"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id", ondelete="CASCADE"), primary_key=True)

    game: Mapped["Game"] = relationship(back_populates="platforms")
    platform: Mapped["Platform"] = relationship(back_populates="games")
