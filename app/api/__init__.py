# app/api/__init__.py
from fastapi import APIRouter
from .routes import games  
from .routes import publishers
from .routes import developers
from .routes import genres
from .routes import platforms
from .routes import price_offers
from .routes import game_genres
from .routes import game_platforms
from .routes import scraper_test

api_router = APIRouter()

# اضافه کردن همه‌ی روت‌ها
api_router.include_router(scraper_test.router, prefix="/test", tags=["Scraper Test"])
api_router.include_router(games.router)
api_router.include_router(publishers.router)
api_router.include_router(developers.router)
api_router.include_router(genres.router)
api_router.include_router(platforms.router)
api_router.include_router(price_offers.router)
api_router.include_router(game_genres.router)
api_router.include_router(game_platforms.router)
