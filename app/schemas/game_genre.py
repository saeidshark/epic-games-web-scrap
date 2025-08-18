from pydantic import BaseModel


class GameGenreBase(BaseModel):
    genre_id: int
    game_id: int


class GameGenreCreate(GameGenreBase):
    pass


class GameGenreUpdate(BaseModel):
    genre_id: int | None = None


class GameGenreOut(GameGenreBase):
    id: int

    class Config:
        from_attributes = True
