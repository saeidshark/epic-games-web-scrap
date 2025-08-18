from __future__ import annotations
import asyncio, random, re
from datetime import datetime
from typing import Iterable
import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_random_exponential

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models import Game, Publisher, Developer, Genre, Platform, PriceOffer

HEADERS_UA = settings.scraper.user_agents or [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36"
]

def _ua() -> dict[str, str]:
    return {"User-Agent": random.choice(HEADERS_UA)}

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=1, max=4))
async def fetch(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.get(url, headers=_ua(), timeout=settings.scraper.request_timeout)
    resp.raise_for_status()
    return resp.text

async def parse_browse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select('[data-component="BrowseGrid"] a[href*="/p/"], a[href*="/product/"]') or soup.select("a.css-1n1")  # fallback
    results: list[dict] = []
    for a in cards[:50]:
        href = a.get("href") or ""
        slug = href.rstrip("/").split("/")[-1]
        title = (a.get_text(strip=True) or slug).strip()
        if not slug:
            continue
        results.append({
            "slug": slug,
            "title": title,
        })
    return results

async def enrich_game_detail(client: httpx.AsyncClient, item: dict) -> dict:
    # تلاش برای دریافت جزئیات صفحهٔ بازی (در صورت وجود)
    url = f'{settings.scraper.base_url}/en-US/p/{item["slug"]}'
    try:
        html = await fetch(client, url)
        soup = BeautifulSoup(html, "lxml")
        desc_el = soup.select_one('[data-component="Description"]') or soup.select_one("div[data-testid='pdp-description']")
        description = desc_el.get_text(" ", strip=True) if desc_el else None

        # تاریخ انتشار (حدسی/وابسته به DOM)
        rd = None
        rd_el = soup.find(string=re.compile(r"Release Date", re.I))
        if rd_el and rd_el.parent:
            rd_text = rd_el.parent.get_text(" ", strip=True)
            m = re.search(r"(\d{4}-\d{2}-\d{2})", rd_text)
            if m:
                rd = m.group(1)

        item.update({
            "description": description,
            "release_date": rd
        })
    except Exception:
        pass
    return item

async def scrape_and_upsert(session: AsyncSession) -> dict:
    """
    اسکرپ لیست بازی‌ها و ثبت/به‌روزرسانی در دیتابیس.
    """
    base = settings.scraper.base_url.rstrip("/")
    browse_url = base + settings.scraper.browse_path

    async with httpx.AsyncClient(base_url=base, follow_redirects=True, http2=True) as client:
        html = await fetch(client, browse_url)
        items = await parse_browse(html)

        # محدودسازی همزمانی و enrichment
        sem = asyncio.Semaphore(settings.scraper.concurrency)
        async def enrich(i):
            async with sem:
                await asyncio.sleep(settings.scraper.delay_between_requests_ms / 1000.0)
                return await enrich_game_detail(client, i)

        detailed = await asyncio.gather(*[enrich(i) for i in items])

    # upsert ساده (slug یکتا)
    created, updated = 0, 0
    for it in detailed:
        slug = it["slug"]
        title = it.get("title") or slug

        result = await session.execute(select(Game).where(Game.slug == slug))
        game = result.scalar_one_or_none()
        if game:
            game.title = title
            game.description = it.get("description")
            # تاریخ انتشار را فقط اگر مقدار معتبر داریم آپدیت کن
            if it.get("release_date"):
                game.release_date = it["release_date"]
            updated += 1
        else:
            game = Game(
                slug=slug,
                title=title,
                description=it.get("description"),
                release_date=it.get("release_date")
            )
            session.add(game)
            created += 1

    await session.commit()
    return {"created": created, "updated": updated, "total": len(detailed)}

#----------------------------------------------------------------------------------------------------------

# from __future__ import annotations

# import asyncio
# import random
# import re
# import socket
# from typing import Optional, List

# import aiodns
# import aiohttp
# from aiohttp import ClientSession, TCPConnector, ClientTimeout
# from bs4 import BeautifulSoup
# from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
# import dns.resolver

# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select

# from app.core.config import settings
# from app.models import Game


# # =========================
# # Headers / UA
# # =========================
# _DEFAULT_UA_POOL = settings.scraper.user_agents or [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36",
# ]

# def _headers() -> dict[str, str]:
#     ua = random.choice(_DEFAULT_UA_POOL)
#     return {
#         "User-Agent": ua,
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Cache-Control": "no-cache",
#         "Pragma": "no-cache",
#         "DNT": "1",
#         "Upgrade-Insecure-Requests": "1",
#     }


# # =========================
# # Smart DNS adapter for aiohttp
# # =========================
# class AioDnsResolverAdapter:
#     def __init__(self, nameservers: Optional[List[str]] = None) -> None:
#         loop = asyncio.get_event_loop()
#         self._resolver = aiodns.DNSResolver(loop=loop, nameservers=nameservers)

#     async def resolve(self, host: str, port: int = 0, family: int = socket.AF_UNSPEC):
#         addrs: list[dict] = []

#         try:
#             if family in (socket.AF_UNSPEC, socket.AF_INET):
#                 a_records = await self._resolver.query(host, "A")
#                 for r in a_records:
#                     addrs.append({
#                         "hostname": host,
#                         "host": r.host,
#                         "port": port,
#                         "family": socket.AF_INET,
#                         "proto": 0,
#                         "flags": 0,
#                     })
#         except Exception:
#             pass

#         try:
#             if family in (socket.AF_UNSPEC, socket.AF_INET6):
#                 aaaa_records = await self._resolver.query(host, "AAAA")
#                 for r in aaaa_records:
#                     addrs.append({
#                         "hostname": host,
#                         "host": r.host,
#                         "port": port,
#                         "family": socket.AF_INET6,
#                         "proto": 0,
#                         "flags": 0,
#                     })
#         except Exception:
#             pass

#         if not addrs:
#             infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
#             for _family, _type, _proto, _canonname, sockaddr in infos:
#                 addrs.append({
#                     "hostname": host,
#                     "host": sockaddr[0],
#                     "port": port,
#                     "family": _family,
#                     "proto": _proto,
#                     "flags": 0,
#                 })

#         uniq = []
#         seen = set()
#         for a in addrs:
#             k = (a["host"], a["family"])
#             if k not in seen:
#                 uniq.append(a)
#                 seen.add(k)
#         return uniq


# # =========================
# # Proxy fetcher
# # =========================
# async def fetch_free_proxies() -> list[str]:
#     """
#     گرفتن پروکسی‌های رایگان از اینترنت (HTTP/HTTPS)
#     """
#     url = "https://www.proxy-list.download/api/v1/get?type=https"
#     async with aiohttp.ClientSession() as s:
#         try:
#             async with s.get(url, timeout=15) as r:
#                 txt = await r.text()
#                 proxies = [f"http://{p.strip()}" for p in txt.splitlines() if p.strip()]
#                 return proxies[:50]  # فقط ۵۰ تا
#         except Exception:
#             return []


# # =========================
# # aiohttp Session builder
# # =========================
# def build_session() -> ClientSession:
#     smart_dns = getattr(settings.scraper, "smart_dns", None) or []
#     resolver = AioDnsResolverAdapter(nameservers=smart_dns) if smart_dns else None

#     timeout = ClientTimeout(
#         total=settings.scraper.request_timeout,
#         connect=min(15, settings.scraper.request_timeout),
#         sock_read=settings.scraper.request_timeout,
#         sock_connect=min(15, settings.scraper.request_timeout),
#     )

#     connector = TCPConnector(
#         resolver=resolver,
#         ssl=None,
#         limit=0,
#         force_close=False,
#         keepalive_timeout=20,
#         ttl_dns_cache=60,
#     )

#     return ClientSession(
#         connector=connector,
#         timeout=timeout,
#         headers=_headers(),
#         trust_env=False,
#         raise_for_status=False,
#     )


# # =========================
# # Fetch with retry + proxy rotation
# # =========================
# _RETRYABLE_STATUSES = {403, 408, 409, 425, 429, 500, 502, 503, 504}

# @retry(
#     stop=stop_after_attempt(6),
#     wait=wait_random_exponential(min=1, max=5),
#     retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
# )
# async def fetch(session: ClientSession, url: str, proxies: list[str]) -> str:
#     proxy = random.choice(proxies) if proxies else None
#     print(f"🌐 Trying proxy: {proxy}")

#     async with session.get(url, proxy=proxy, allow_redirects=True) as resp:
#         status = resp.status
#         text = await resp.text(errors="ignore")

#         if status in _RETRYABLE_STATUSES:
#             raise aiohttp.ClientResponseError(
#                 resp.request_info, resp.history, status=status, message=f"retryable {status}"
#             )
#         if status >= 400:
#             raise aiohttp.ClientResponseError(
#                 resp.request_info, resp.history, status=status, message=text[:300]
#             )
#         return text


# # =========================
# # Parsers
# # =========================
# async def parse_browse(html: str) -> list[dict]:
#     soup = BeautifulSoup(html, "lxml")
#     cards = soup.select('[data-component="BrowseGrid"] a[href*="/p/"], a[href*="/product/"]')
#     results: list[dict] = []
#     for a in cards[:50]:
#         href = a.get("href") or ""
#         slug = href.rstrip("/").split("/")[-1]
#         title = (a.get_text(strip=True) or slug).strip()
#         if slug:
#             results.append({"slug": slug, "title": title})
#     return results


# async def enrich_game_detail(session: ClientSession, item: dict, proxies: list[str]) -> dict:
#     url = f'{settings.scraper.base_url.rstrip("/")}/en-US/p/{item["slug"]}'
#     try:
#         html = await fetch(session, url, proxies)
#         soup = BeautifulSoup(html, "lxml")
#         desc_el = soup.select_one('[data-component="Description"]') or soup.select_one("div[data-testid='pdp-description']")
#         description = desc_el.get_text(" ", strip=True) if desc_el else None
#         item.update({"description": description})
#     except Exception as e:
#         print(f"❌ detail failed for {item['slug']}: {e}")
#     return item


# # =========================
# # Main scraper
# # =========================
# async def scrape_and_upsert(session_db: AsyncSession) -> dict:
#     base = settings.scraper.base_url.rstrip("/")
#     browse_url = base + settings.scraper.browse_path

#     created, updated = 0, 0

#     proxies = await fetch_free_proxies()
#     if not proxies:
#         print("⚠️ No free proxies found, will use direct connection.")

#     async with build_session() as session_http:
#         html = await fetch(session_http, browse_url, proxies)
#         items = await parse_browse(html)

#         sem = asyncio.Semaphore(settings.scraper.concurrency)

#         async def enrich(i):
#             async with sem:
#                 await asyncio.sleep(settings.scraper.delay_between_requests_ms / 1000.0)
#                 return await enrich_game_detail(session_http, i, proxies)

#         detailed = await asyncio.gather(*[enrich(i) for i in items], return_exceptions=False)

#     for it in detailed:
#         slug = it["slug"]
#         title = it.get("title") or slug
#         result = await session_db.execute(select(Game).where(Game.slug == slug))
#         game = result.scalar_one_or_none()

#         if game:
#             game.title = title
#             game.description = it.get("description")
#             updated += 1
#         else:
#             game = Game(slug=slug, title=title, description=it.get("description"))
#             session_db.add(game)
#             created += 1

#     await session_db.commit()
#     return {"created": created, "updated": updated, "total": len(detailed)}


# # =========================
# # DNS debug helper
# # =========================
# async def dns_debug(host: str = "store.epicgames.com") -> dict:
#     smart_ips = []
#     try:
#         r = dns.resolver.Resolver()
#         if getattr(settings.scraper, "smart_dns", None):
#             r.nameservers = settings.scraper.smart_dns
#         ans = r.resolve(host, "A")
#         smart_ips = [rr.to_text() for rr in ans]
#     except Exception as e:
#         smart_ips = [f"error: {e}"]

#     sys_ips = []
#     try:
#         infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
#         sys_ips = list(dict.fromkeys([x[4][0] for x in infos]))
#     except Exception as e:
#         sys_ips = [f"error: {e}"]

#     return {
#         "host": host,
#         "smart_dns": getattr(settings.scraper, "smart_dns", None),
#         "smart_resolve": smart_ips,
#         "system_resolve": sys_ips
#     }
