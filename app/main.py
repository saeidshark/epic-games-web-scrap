from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router
from app.db.session import engine
from app.db.base import Base

app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    version="1.0.0",
    contact={"name": "API"},
)

# CORS آزاد برای Swagger UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ایجاد جداول در استارتاپ (برای سادگی؛ در عمل بهتر است Alembic)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(api_router, prefix="/api")
