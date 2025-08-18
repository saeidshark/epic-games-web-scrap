from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.game_genre import GameGenre
from app.utils.deps import get_db

router = APIRouter(prefix="/game_genres", tags=["Game Genres"])

@router.post("/")
async def create_game_genre(game_id: int, genre_id: int, db: AsyncSession = Depends(get_db)):
    game_genre = GameGenre(game_id=game_id, genre_id=genre_id)
    db.add(game_genre)
    await db.commit()
    await db.refresh(game_genre)
    return game_genre

@router.get("/{link_id}")
async def get_game_genre(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GameGenre).where(GameGenre.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Game-Genre link not found")
    return link

@router.get("/")
async def get_all_game_genres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GameGenre))
    return result.scalars().all()

@router.delete("/{link_id}")
async def delete_game_genre(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GameGenre).where(GameGenre.id == link_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Game-Genre link not found")
    await db.delete(link)
    await db.commit()
    return {"message": "Game-Genre link deleted"}

@router.delete("/")
async def delete_all_game_genres(db: AsyncSession = Depends(get_db)):
    await db.execute("DELETE FROM game_genres")
    await db.commit()
    return {"message": "All game-genre links deleted"}
