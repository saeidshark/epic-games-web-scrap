from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.price_offer import PriceOffer
from app.utils.deps import get_db
from datetime import date

router = APIRouter(prefix="/price_offers", tags=["Price Offers"])

@router.post("/")
async def create_price_offer(game_id: int, price: float, start_date: date, end_date: date, db: AsyncSession = Depends(get_db)):
    price_offer = PriceOffer(game_id=game_id, price=price, start_date=start_date, end_date=end_date)
    db.add(price_offer)
    await db.commit()
    await db.refresh(price_offer)
    return price_offer

@router.get("/{offer_id}")
async def get_price_offer(offer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceOffer).where(PriceOffer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Price offer not found")
    return offer

@router.get("/")
async def get_all_price_offers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceOffer))
    return result.scalars().all()

@router.put("/{offer_id}")
async def update_price_offer(offer_id: int, price: float, start_date: date, end_date: date, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceOffer).where(PriceOffer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Price offer not found")
    offer.price = price
    offer.start_date = start_date
    offer.end_date = end_date
    await db.commit()
    await db.refresh(offer)
    return offer

@router.delete("/{offer_id}")
async def delete_price_offer(offer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceOffer).where(PriceOffer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Price offer not found")
    await db.delete(offer)
    await db.commit()
    return {"message": "Price offer deleted"}

@router.delete("/")
async def delete_all_price_offers(db: AsyncSession = Depends(get_db)):
    await db.execute("DELETE FROM price_offers")
    await db.commit()
    return {"message": "All price offers deleted"}
