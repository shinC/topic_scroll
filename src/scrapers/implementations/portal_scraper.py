import asyncio
from datetime import datetime, timezone
import re
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
    공지사항/복지서비스/새소식을 정밀하게 수집하는 웹 크롤러 구현체
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

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """날짜 문자열 (YYYY-MM-DD 또는 YYYY.MM.DD) 파싱"""
        if not date_str:
            return None
        date_str = date_str.strip()
        match = re.search(r"(\d{4})[.-](\d{2})[.-](\d{2})", date_str)
        if match:
            y, m, d = match.groups()
            try:
                return datetime(int(y), int(m), int(d), tzinfo=timezone.utc)
            except ValueError:
                pass
        return None

    async def _parse_gov24(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """정부24 정책 및 보조금24 소식 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        publisher = source_cfg.get("publisher", "정부24")
        category = source_cfg.get("category", "정부정책")

        # 메인 URL("https://www.gov.kr/portal/main" 등)인 경우 정책 목록 페이지로 자동 전환
        if "main" in url or "gvrnPolicy" not in url:
            target_url = "https://www.gov.kr/portal/gvrnPolicy?srchOrder=&pageIndex=1&policyType=G00301&streamYn=&publishOrgNm=&blgCd=&slgCd=&srchBlgCd=&srchSlgCd=&srchOrgGroup=&srchOriginOrg=&srchPeriodOption=all&srchStDtFmt=&srchEdDtFmt=&searchField=3&srchTxt=&srchTxt2="
        else:
            target_url = url

        articles: List[Article] = []
        response = await client.get(target_url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # goViewSubmit 링크를 포함한 정책 뉴스 항목 파싱
        seen_titles = set()
        for a in soup.find_all("a", href=re.compile(r"goViewSubmit")):
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            policy_id_match = re.search(r"[\'\"]([^\'\"]+)[\'\"]", href)
            policy_id = policy_id_match.group(1) if policy_id_match else ""

            # 날짜 추출 (상위 컨테이너 또는 text regex)
            parent = a.find_parent("li") or a.find_parent("tr") or a.find_parent("div")
            date_str = None
            if parent:
                d_match = re.search(r"202\d[.-]\d{2}[.-]\d{2}", parent.get_text())
                if d_match:
                    date_str = d_match.group(0)

            pub_date = self._parse_date(date_str)
            detail_url = (
                f"https://www.gov.kr/portal/gvrnPolicy/gvrnPolicyDetail?gvrnPolicyId={policy_id}"
                if policy_id
                else target_url
            )

            article = Article(
                id=f"gov24_{policy_id or abs(hash(title))}",
                title=title,
                content=f"[{publisher}] {title}",
                url=detail_url,
                site_name=publisher,
                published_at=pub_date,
                category=category,
                extra_meta={
                    "portal_id": portal_id,
                    "purpose": source_cfg.get("purpose", []),
                },
            )
            articles.append(article)

        return articles

    async def _parse_work24(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """고용24 공지사항/새소식 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        publisher = source_cfg.get("publisher", "고용24")
        category = source_cfg.get("category", "고용정책")

        articles: List[Article] = []
        response = await client.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        seen_titles = set()
        for tr in soup.select("table tbody tr"):
            tds = tr.find_all("td")
            if len(tds) < 2:
                continue

            a = tr.find("a")
            title = a.get_text(strip=True) if a else tds[0].get_text(strip=True)
            date_str = tds[-1].get_text(strip=True)

            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            pub_date = self._parse_date(date_str)

            href = a.get("href", "") if a else ""
            onclick = a.get("onclick", "") if a else ""
            id_match = re.search(r"[\'\"]([^\'\"]+)[\'\"]", onclick or href)
            detail_id = id_match.group(1) if id_match else ""

            if detail_id and detail_id.isdigit():
                detail_url = f"https://www.work24.go.kr/wk/r/g/1110/retrieveEmpNewsDtl.do?empNewsId={detail_id}"
            else:
                detail_url = url

            article = Article(
                id=f"work24_{detail_id or abs(hash(title))}",
                title=title,
                content=f"[{publisher}] {title}",
                url=detail_url,
                site_name=publisher,
                published_at=pub_date,
                category=category,
                extra_meta={
                    "portal_id": portal_id,
                    "purpose": source_cfg.get("purpose", []),
                },
            )
            articles.append(article)

        return articles

    async def _parse_bokjiro(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """복지로 중앙/지방 복지서비스 JSON API 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        portal_name = source_cfg.get("name", "")
        publisher = source_cfg.get("publisher", "보건복지부")
        category = source_cfg.get("category", "복지정책")

        tab_id = "1"
        if "tabId=2" in url or "지방" in portal_name:
            tab_id = "2"

        api_url = "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/retrieveWlfareInfoList.do"
        payload = {
            "dmSearch": {
                "page": "1",
                "tabId": tab_id,
                "orderBy": "date",
            }
        }

        # Bokjiro API requires browser User-Agent and session cookie to pass WAF
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        articles: List[Article] = []

        try:
            async with httpx.AsyncClient(headers={"User-Agent": ua}, follow_redirects=True, timeout=settings.REQUEST_TIMEOUT) as bokji_client:
                await bokji_client.get(url)
                response = await bokji_client.post(
                    api_url,
                    headers={
                        "Content-Type": "application/json;charset=UTF-8",
                        "Accept": "application/json, text/javascript, */*",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("dsWlfareList", [])
        except Exception as e:
            logger.warning(f"복지로 API 요청 실패 ({url}): {str(e)}")
            items = []

        for item in items:
            title = item.get("wlfarInfoNm", "").strip()
            if not title:
                continue

            info_id = item.get("wlfarInfoId", "")
            date_str = item.get("crtDtm", "")
            summary = item.get("wlfarInfoOutlCntn", "")
            dept_name = item.get("bizChrgDeptNm", publisher)

            pub_date = self._parse_date(date_str)
            detail_url = f"https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/moveTWAT52005M.do?tabId={tab_id}&wlfarInfoId={info_id}"

            article = Article(
                id=f"bokjiro_{info_id or abs(hash(title))}",
                title=title,
                content=summary or f"[{dept_name}] {title}",
                url=detail_url,
                site_name=dept_name,
                published_at=pub_date,
                category=category,
                summary=summary[:300] if summary else None,
                extra_meta={
                    "portal_id": portal_id,
                    "tab_id": tab_id,
                    "purpose": source_cfg.get("purpose", []),
                },
            )
            articles.append(article)

        return articles

    async def _parse_molit(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """국토교통부 보도자료 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        publisher = source_cfg.get("publisher", "국토교통부")
        category = source_cfg.get("category", "부동산/교통")

        articles: List[Article] = []
        response = await client.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        seen_titles = set()
        for tr in soup.select("table.tbl_lb tbody tr"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue

            a = tds[1].find("a")
            if not a:
                continue

            title = a.get_text(strip=True)
            sub_cat = tds[2].get_text(strip=True)
            date_str = tds[3].get_text(strip=True)

            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            pub_date = self._parse_date(date_str)

            href = a.get("href", "")
            id_match = re.search(r"[\'\"]([^\'\"]+)[\'\"]", href)
            item_id = id_match.group(1) if id_match else ""

            if item_id:
                detail_url = f"https://www.molit.go.kr/USR/NEWS/m_71/dtl.jsp?id={item_id}"
            else:
                detail_url = url

            article = Article(
                id=f"molit_{item_id or abs(hash(title))}",
                title=title,
                content=f"[{publisher} {sub_cat}] {title}",
                url=detail_url,
                site_name=publisher,
                published_at=pub_date,
                category=category,
                extra_meta={
                    "portal_id": portal_id,
                    "sub_category": sub_cat,
                    "purpose": source_cfg.get("purpose", []),
                },
            )
            articles.append(article)

        return articles

    async def parse_portal_source(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """
        개별 포털 사이트 ID 및 URL을 판별하여 해당 전용 파서로 분기 수집합니다.
        """
        portal_id = source_cfg.get("id", "")
        url = source_cfg.get("url", "")
        portal_name = source_cfg.get("name", "")

        try:
            if "gov24" in portal_id or "gov.kr" in url:
                return await self._parse_gov24(source_cfg, client)
            elif "work24" in portal_id or "work24.go.kr" in url:
                return await self._parse_work24(source_cfg, client)
            elif "bokjiro" in portal_id or "bokjiro.go.kr" in url:
                return await self._parse_bokjiro(source_cfg, client)
            elif "molit" in portal_id or "molit.go.kr" in url:
                return await self._parse_molit(source_cfg, client)
            else:
                logger.warning(f"전용 파서 없음, 정부24 파서 기준 수집: [{portal_name}] ({url})")
                return await self._parse_gov24(source_cfg, client)
        except Exception as e:
            logger.warning(f"포털 크롤링 실패 [{portal_name}] ({url}): {str(e)}")
            return []

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

