from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.models.platform import Platform
from app.schemas.platform import PlatformCreate, PlatformUpdate, PlatformOut

router = APIRouter(prefix="/platforms", tags=["Platforms"])


@router.get("/", response_model=list[PlatformOut])
async def get_platforms(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Platform))
    return result.scalars().all()


@router.get("/{platform_id}", response_model=PlatformOut)
async def get_platform(platform_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Platform).where(Platform.id == platform_id))
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform


@router.post("/", response_model=PlatformOut)
async def create_platform(data: PlatformCreate, db: AsyncSession = Depends(get_session)):
    platform = Platform(**data.dict())
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    return platform


@router.put("/{platform_id}", response_model=PlatformOut)
async def update_platform(platform_id: int, data: PlatformUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Platform).where(Platform.id == platform_id))
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    platform.name = data.name
    await db.commit()
    await db.refresh(platform)
    return platform


@router.delete("/{platform_id}")
async def delete_platform(platform_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Platform).where(Platform.id == platform_id))
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    await db.delete(platform)
    await db.commit()
    return {"detail": "Platform deleted"}


@router.delete("/")
async def delete_all_platforms(db: AsyncSession = Depends(get_session)):
    await db.execute("DELETE FROM platforms")
    await db.commit()
    return {"detail": "All platforms deleted"}
