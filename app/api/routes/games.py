from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from app.utils.deps import get_db
from app.models import Game
from app.schemas.game import GameCreate, GameUpdate, GameOut
from app.services.scraper import scrape_and_upsert

router = APIRouter(prefix="/games", tags=["games"])

@router.get("/", response_model=List[GameOut])
async def list_games(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    res = await db.execute(select(Game).offset(offset).limit(limit))
    return res.scalars().all()

@router.get("/{game_id}", response_model=GameOut)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Game).where(Game.id == game_id))
    game = res.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.post("/", response_model=GameOut, status_code=201)
async def create_game(payload: GameCreate, db: AsyncSession = Depends(get_db)):
    # جلوگیری از تکرار slug
    exists = await db.execute(select(Game).where(Game.slug == payload.slug))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")
    game = Game(**payload.model_dump())
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game

@router.put("/{game_id}", response_model=GameOut)
async def update_game(game_id: int, payload: GameUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Game).where(Game.id == game_id))
    game = res.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(game, k, v)
    await db.commit()
    await db.refresh(game)
    return game

@router.delete("/{game_id}", status_code=204)
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Game).where(Game.id == game_id))
    game = res.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    await db.delete(game)
    await db.commit()
    return

@router.delete("/", status_code=204)
async def delete_all_games(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Game))
    await db.commit()
    return

# استفاده از Thread به‌عنوان دمو (Thread برای پردازش موازی سبک)
from threading import Thread
def _scrape_thread(db_factory):
    import anyio
    async def _run():
        async for db in db_factory():
            await scrape_and_upsert(db)
            break
    anyio.run(_run)

@router.post("/refresh", summary="Scrape & upsert from Epic Games (threaded)")
async def refresh_games(background: bool = True, db: AsyncSession = Depends(get_db)):
    """
    اگر background=True باشد با Thread اجرا می‌شود.
    """
    if background:
        t = Thread(target=_scrape_thread, args=(get_db,))
        t.daemon = True
        t.start()
        return {"status": "started in background thread"}
    else:
        result = await scrape_and_upsert(db)
        return {"status": "done", **result}
