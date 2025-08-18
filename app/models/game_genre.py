from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class GameGenre(Base):
    __tablename__ = "game_genres"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)

    game: Mapped["Game"] = relationship(back_populates="genres")
    genre: Mapped["Genre"] = relationship(back_populates="games")
