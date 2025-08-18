from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.game_platform import GamePlatform
from app.utils.deps import get_db

router = APIRouter(prefix="/game_platforms", tags=["Game Platforms"])

@router.post("/")
async def create_game_platform(game_id: int, platform_id: int, db: AsyncSession = Depends(get_db)):
    game_platform = GamePlatform(game_id=game_id, platform_id=platform_id)
    db.add(game_platform)
    await db.commit()
    await db.refresh(game_platform)
    return game_platform

@router.get("/{link_id}")
async def get_game_platform(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GamePlatform).where(GamePlatform.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Game-Platform link not found")
    return link

@router.get("/")
async def get_all_game_platforms(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GamePlatform))
    return result.scalars().all()

@router.delete("/{link_id}")
async def delete_game_platform(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GamePlatform).where(GamePlatform.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Game-Platform link not found")
    await db.delete(link)
    await db.commit()
    return {"message": "Game-Platform link deleted"}

@router.delete("/")
async def delete_all_game_platforms(db: AsyncSession = Depends(get_db)):
    await db.execute("DELETE FROM game_platforms")
    await db.commit()
    return {"message": "All game-platform links deleted"}
