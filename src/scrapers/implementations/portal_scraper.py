import asyncio
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup

from config import load_portal_config, settings
from models.article import Article, ScrapingResult
from scrapers.base import BaseScraper
from scrapers.registry import scraper_registry
from utils.logger import logger


@scraper_registry.register
class PortalScraper(BaseScraper):
    """
    portal.yaml 에 정의된 정부24, 고용24, 복지로, 국토교통부 등 주요 포털의
    공지사항/새소식을 수집하는 웹 크롤러 구현체
    """

    @property
    def name(self) -> str:
        return "portal_news"

    @property
    def site_name(self) -> str:
        return "주요 포털 새소식"

    @property
    def base_url(self) -> str:
        return "portal_sources"

    async def parse_portal_source(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """
        개별 포털 사이트의 공지/소식 목록 페이지를 요청하고 파싱합니다.
        """
        url = source_cfg.get("url")
        portal_name = source_cfg.get("name")
        publisher = source_cfg.get("publisher", portal_name)
        category = source_cfg.get("category", "정부정책")

        articles: List[Article] = []
        try:
            response = await client.get(url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # 각 대표 포털별 셀렉터 패턴 탐색 및 범용 링크 extraction
            # a 태그 중 텍스트 길이가 유의미한 링크 추출
            link_elements = soup.select("a[href]")
            seen_titles = set()

            for a in link_elements:
                title = a.get_text(strip=True)
                href = a.get("href", "").strip()

                # 의미없는 짧은 링크나 자바스크립트 링크 스킵
                if not title or len(title) < 5 or href.startswith("javascript:") or href == "#":
                    continue

                if title in seen_titles:
                    continue
                seen_titles.add(title)

                full_url = urljoin(url, href)

                article = Article(
                    id=f"portal_{hash(full_url)}",
                    title=title,
                    content=f"[{publisher}] {title}",
                    url=full_url,
                    site_name=publisher,
                    published_at=datetime.now(),
                    category=category,
                    extra_meta={
                        "portal_id": source_cfg.get("id"),
                        "purpose": source_cfg.get("purpose", []),
                    },
                )
                articles.append(article)

                if len(articles) >= 20:  # 사이트당 최대 20개로 제한
                    break

        except Exception as e:
            logger.warning(f"포털 크롤링 실패 [{portal_name}] ({url}): {str(e)}")

        return articles

    async def parse(self, html: str, url: str) -> List[Article]:
        return []

    async def run(self, client: Optional[httpx.AsyncClient] = None) -> ScrapingResult:
        """
        portal.yaml에 등록된 포털 사이트를 수집합니다.
        """
        start_time = datetime.now()
        config = load_portal_config()
        portal_sources = [
            p for p in config.get("portal_sources", []) if p.get("enabled", True)
        ]

        logger.info(f"[포털 크롤러] 총 {len(portal_sources)}개 사이트 수집 시작...")

        all_articles: List[Article] = []
        close_client = False
        if client is None:
            client = httpx.AsyncClient(
                headers={"User-Agent": settings.DEFAULT_USER_AGENT},
                follow_redirects=True,
            )
            close_client = True

        try:
            semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

            async def sem_fetch(p_cfg):
                async with semaphore:
                    return await self.parse_portal_source(p_cfg, client)

            tasks = [sem_fetch(p_cfg) for p_cfg in portal_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    all_articles.extend(res)

        finally:
            if close_client:
                await client.aclose()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"[포털 크롤러] 수집 완료: 총 {len(all_articles)}개 항목 수집됨 ({elapsed:.2f}초 소요)"
        )

        return ScrapingResult(
            site_name=self.site_name,
            success=True,
            articles=all_articles,
            total_count=len(all_articles),
            execution_time_seconds=round(elapsed, 2),
        )
