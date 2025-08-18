from pydantic import BaseModel


class GamePlatformBase(BaseModel):
    platform_id: int
    game_id: int


class GamePlatformCreate(GamePlatformBase):
    pass


class GamePlatformUpdate(BaseModel):
    platform_id: int | None = None


class GamePlatformOut(GamePlatformBase):
    id: int

    class Config:
        from_attributes = True
