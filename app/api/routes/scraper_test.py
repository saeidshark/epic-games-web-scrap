from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.deps import get_db
from app.services.scraper import scrape_and_upsert, dns_debug

router = APIRouter()

@router.post("/scrape-test")
async def scrape_test(db: AsyncSession = Depends(get_db)):
    result = await scrape_and_upsert(db)
    return result

@router.get("/dns-check")
async def dns_check():
    return await dns_debug("store.epicgames.com")
