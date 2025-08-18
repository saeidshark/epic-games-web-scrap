from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.models.publisher import Publisher

router = APIRouter(prefix="/publishers", tags=["publishers"])

@router.get("/")
async def get_all(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Publisher))
    return result.scalars().all()

@router.get("/{publisher_id}")
async def get_one(publisher_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Publisher).where(Publisher.id == publisher_id))
    publisher = result.scalar_one_or_none()
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return publisher

@router.post("/")
async def create(publisher: dict, db: AsyncSession = Depends(get_session)):
    new_publisher = Publisher(**publisher)
    db.add(new_publisher)
    await db.commit()
    await db.refresh(new_publisher)
    return new_publisher

@router.put("/{publisher_id}")
async def update(publisher_id: int, publisher: dict, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Publisher).where(Publisher.id == publisher_id))
    db_publisher = result.scalar_one_or_none()
    if not db_publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    for key, value in publisher.items():
        setattr(db_publisher, key, value)
    await db.commit()
    await db.refresh(db_publisher)
    return db_publisher

@router.delete("/{publisher_id}")
async def delete_one(publisher_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Publisher).where(Publisher.id == publisher_id))
    publisher = result.scalar_one_or_none()
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    await db.delete(publisher)
    await db.commit()
    return {"detail": "Publisher deleted"}

@router.delete("/")
async def delete_all(db: AsyncSession = Depends(get_session)):
    await db.execute("DELETE FROM publishers")
    await db.commit()
    return {"detail": "All publishers deleted"}
