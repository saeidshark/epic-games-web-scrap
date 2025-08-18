from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.models.developer import Developer
from app.schemas.developer import DeveloperOut, DeveloperCreate, DeveloperUpdate

router = APIRouter(prefix="/developers", tags=["Developers"])

@router.get("/", response_model=list[DeveloperOut])
async def get_developers(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Developer))
    return result.scalars().all()

@router.get("/{developer_id}", response_model=DeveloperOut)
async def get_developer(developer_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Developer).where(Developer.id == developer_id))
    developer = result.scalar_one_or_none()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    return developer

@router.post("/", response_model=DeveloperOut)
async def create_developer(developer: DeveloperCreate, db: AsyncSession = Depends(get_session)):
    new_dev = Developer(**developer.dict())
    db.add(new_dev)
    await db.commit()
    await db.refresh(new_dev)
    return new_dev

@router.put("/{developer_id}", response_model=DeveloperOut)
async def update_developer(developer_id: int, updated: DeveloperUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Developer).where(Developer.id == developer_id))
    developer = result.scalar_one_or_none()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    developer.name = updated.name
    await db.commit()
    await db.refresh(developer)
    return developer

@router.delete("/{developer_id}")
async def delete_developer(developer_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Developer).where(Developer.id == developer_id))
    developer = result.scalar_one_or_none()
    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")
    await db.delete(developer)
    await db.commit()
    return {"detail": "Developer deleted"}

@router.delete("/")
async def delete_all_developers(db: AsyncSession = Depends(get_session)):
    await db.execute("DELETE FROM developers")
    await db.commit()
    return {"detail": "All developers deleted"}
