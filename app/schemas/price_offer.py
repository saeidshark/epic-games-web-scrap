from datetime import date
from pydantic import BaseModel


class PriceOfferBase(BaseModel):
    price: float
    start_date: date
    end_date: date | None = None


class PriceOfferCreate(PriceOfferBase):
    game_id: int


class PriceOfferUpdate(BaseModel):
    price: float | None = None
    start_date: date | None = None
    end_date: date | None = None


class PriceOfferOut(PriceOfferBase):
    id: int
    game_id: int

    class Config:
        from_attributes = True
