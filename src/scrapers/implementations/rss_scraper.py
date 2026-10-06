import asyncio
from datetime import datetime, timezone
from time import mktime
from typing import List, Optional
import feedparser
import httpx

from config import load_feeds_config, settings
from models.article import Article, ScrapingResult
from scrapers.base import BaseScraper
from scrapers.registry import scraper_registry
from utils.logger import logger


@scraper_registry.register
class RSSScraper(BaseScraper):
    """
    feeds.yaml 에 정의된 모든 RSS 피드에서 뉴스를 수집하는 통합 RSS 스크래퍼
    """

    def __init__(self, max_items_per_feed: int = 20):
        self._max_items_per_feed = max_items_per_feed

    @property
    def name(self) -> str:
        return "rss_news"

    @property
    def site_name(self) -> str:
        return "RSS 뉴스 모음"

    @property
    def base_url(self) -> str:
        return "rss_feeds"

    async def parse_single_feed(
        self, feed_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """
        개별 RSS 피드를 요청하고 파싱합니다.
        """
        url = feed_cfg.get("url")
        feed_name = feed_cfg.get("name", feed_cfg.get("id"))
        publisher = feed_cfg.get("publisher", "알 수 없음")
        category = feed_cfg.get("category", "뉴스")

        articles: List[Article] = []
        try:
            feed_headers = None
            if "hankyung.com" in (url or ""):
                feed_headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; FeedFetcher-Google; +http://www.google.com/feedfetcher.html)",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                }

            content = None
            try:
                response = await client.get(
                    url,
                    headers=feed_headers,
                    timeout=settings.REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                content = response.text
            except (httpx.HTTPStatusError, httpx.RequestError) as http_err:
                # 403 차단 또는 SSL/연결 예외 발생 시 curl_cffi 임퍼소네이션 또는 피드 리더 UA 유연 폴백으로 재시도
                try:
                    from curl_cffi import requests as curl_requests
                    def _fetch_curl_cffi(target_url: str):
                        return curl_requests.get(
                            target_url,
                            impersonate="chrome",
                            timeout=int(settings.REQUEST_TIMEOUT),
                        )
                    resp = await asyncio.to_thread(_fetch_curl_cffi, url)
                    if resp.status_code == 200:
                        content = resp.text
                except Exception as cf_err:
                    logger.debug(f"curl_cffi 재시도 실패 [{feed_name}]: {cf_err}")

                if not content:
                    fallback_headers = {
                        "User-Agent": "Mozilla/5.0 (compatible; FeedFetcher-Google; +http://www.google.com/feedfetcher.html)",
                        "Accept": "application/rss+xml, application/xml, text/xml, */*",
                    }
                    async with httpx.AsyncClient(
                        headers=fallback_headers,
                        follow_redirects=True,
                        verify=False,
                        timeout=settings.REQUEST_TIMEOUT,
                    ) as fallback_client:
                        response = await fallback_client.get(url)
                        response.raise_for_status()
                        content = response.text

            if not content:
                return []

            # feedparser 로 XML / RSS / Atom 분석
            feed = feedparser.parse(content)
            entries = feed.entries[: self._max_items_per_feed]

            for entry in entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                if not title or not link:
                    continue

                # 날짜 파싱
                published_at = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_at = datetime.fromtimestamp(
                        mktime(entry.published_parsed), tz=timezone.utc
                    )
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published_at = datetime.fromtimestamp(
                        mktime(entry.updated_parsed), tz=timezone.utc
                    )

                # 요약 / 본문 텍스트 정제
                raw_summary = entry.get("summary", entry.get("description", ""))
                clean_summary = raw_summary
                if raw_summary and ("<" in raw_summary and ">" in raw_summary):
                    try:
                        clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text(separator=" ", strip=True)
                    except Exception:
                        clean_summary = raw_summary
                clean_summary = " ".join(clean_summary.split()) if clean_summary else ""

                content_body = clean_summary[:300] if clean_summary else title

                article = Article(
                    id=f"rss_{entry.get('id', link)}",
                    title=title,
                    content=content_body,
                    url=link,
                    site_name=publisher,
                    author=entry.get("author", None),
                    published_at=published_at,
                    category=category,
                    summary=content_body,
                    extra_meta={
                        "feed_id": feed_cfg.get("id"),
                        "feed_name": feed_name,
                        "subcategory": feed_cfg.get("subcategory"),
                    },
                )
                articles.append(article)

        except Exception as e:
            logger.warning(f"RSS 피드 수집 실패 [{feed_name}] ({url}): {str(e)}")

        return articles

    async def parse(self, html: str, url: str) -> List[Article]:
        # run() 메서드를 오버라이드하므로 parse는 기본 구동에 쓰이지 않음
        return []

    async def run(self, client: Optional[httpx.AsyncClient] = None) -> ScrapingResult:
        """
        feeds.yaml에 등록된 모든 비활성화되지 않은 RSS 피드를 병렬 수집합니다.
        """
        start_time = datetime.now()
        config = load_feeds_config()
        rss_feeds = [
            f for f in config.get("rss_feeds", []) if f.get("enabled", True)
        ]

        logger.info(f"[RSS 뉴스 수집기] 총 {len(rss_feeds)}개 피드 수집 시작...")

        all_articles: List[Article] = []
        close_client = False
        if client is None:
            client = httpx.AsyncClient(
                headers={"User-Agent": settings.DEFAULT_USER_AGENT},
                follow_redirects=True,
            )
            close_client = True

        try:
            # 5개씩 세마포어로 동시성 제어
            semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

            async def sem_fetch(f_cfg):
                async with semaphore:
                    return await self.parse_single_feed(f_cfg, client)

            tasks = [sem_fetch(f_cfg) for f_cfg in rss_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    all_articles.extend(res)

        finally:
            if close_client:
                await client.aclose()

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"[RSS 뉴스 수집기] 수집 완료: 총 {len(all_articles)}개 기사 수집됨 ({elapsed:.2f}초 소요)"
        )

        return ScrapingResult(
            site_name=self.site_name,
            success=True,
            articles=all_articles,
            total_count=len(all_articles),
            execution_time_seconds=round(elapsed, 2),
        )
