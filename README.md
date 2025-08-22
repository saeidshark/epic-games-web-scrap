# epic-games-web-scrap
python

NOTICE : THIS PROJECT DOES NOT WORK IN SANCTIONED COUNTRIES.(IRAN , CHINA , RUSSIA , NORTH KOREA , ...)

database name : epic_games
install packages:
fastapi>=0.110,<1.0
uvicorn[standard]>=0.30,<0.31
SQLAlchemy>=2.0,<2.1
asyncpg>=0.29,<0.30
alembic>=1.13,<1.14
pydantic>=2.5,<3
pydantic-settings>=2.3,<3
httpx>=0.27,<0.28
beautifulsoup4>=4.12,<5
lxml>=5.2,<6
PyYAML>=6.0,<7
python-dotenv>=1.0,<2
tenacity>=8.2,<9
httpx[http2]
aiohttp
aiodns 
dnspython

follow thes commands in cmd or terminal first :

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

python -m venv .venv

.\.venv\Scripts\activate

at last if you installed uvicorn use tis command 
   uvicorn main:app --reload
otherwise just run code
