# from pydantic import BaseModel, Field
# from typing import Optional, List

# class GameBase(BaseModel):
#     slug: str = Field(..., examples=["fortnite"])
#     title: str
#     description: Optional[str] = None
#     release_date: Optional[str] = Field(None, description="YYYY-MM-DD")
#     publisher_id: Optional[int] = None
#     developer_id: Optional[int] = None

# class GameCreate(GameBase):
#     pass

# class GameUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     release_date: Optional[str] = None
#     publisher_id: Optional[int] = None
#     developer_id: Optional[int] = None

# class GameOut(GameBase):
#     id: int

#     class Config:
#         from_attributes = True


from pydantic import BaseModel
from datetime import date

class GameBase(BaseModel):
    title: str
    description: str | None = None
    release_date: date | None = None
    publisher_id: int | None = None
    developer_id: int | None = None

class GameCreate(GameBase):
    pass

class GameUpdate(GameBase):
    pass

class GameOut(GameBase):
    id: int

    class Config:
      from_attributes = True

