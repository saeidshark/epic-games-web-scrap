from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_session
from app.models.genre import Genre
from app.schemas.genre import GenreOut, GenreCreate, GenreUpdate

router = APIRouter(prefix="/genres", tags=["Genres"])

@router.get("/", response_model=list[GenreOut])
async def get_genres(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Genre))
    return result.scalars().all()

@router.get("/{genre_id}", response_model=GenreOut)
async def get_genre(genre_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Genre).where(Genre.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

@router.post("/", response_model=GenreOut)
async def create_genre(genre: GenreCreate, db: AsyncSession = Depends(get_session)):
    new_genre = Genre(**genre.dict())
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return new_genre

@router.put("/{genre_id}", response_model=GenreOut)
async def update_genre(genre_id: int, updated: GenreUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Genre).where(Genre.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    genre.name = updated.name
    await db.commit()
    await db.refresh(genre)
    return genre

@router.delete("/{genre_id}")
async def delete_genre(genre_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Genre).where(Genre.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    await db.delete(genre)
    await db.commit()
    return {"detail": "Genre deleted"}

@router.delete("/")
async def delete_all_genres(db: AsyncSession = Depends(get_session)):
    await db.execute("DELETE FROM genres")
    await db.commit()
    return {"detail": "All genres deleted"}
