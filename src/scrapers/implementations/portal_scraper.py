import asyncio
from datetime import datetime, timezone, timedelta
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
    portal.yaml 에 정의된 정부24, 고용24, 복지로, 국토교통부, 대한민국 정책브리핑, 보건복지부, 블라인드, 포모스 등 주요 포털의
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
        """정부24 정책 소식 수집 파서"""
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
        """복지로 중앙/지방 복지서비스 수집 파서 (JSON API & HTML 폴백)"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        portal_name = source_cfg.get("name", "복지로")
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

        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        articles: List[Article] = []
        items = []

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
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("dsWlfareList", [])
                else:
                    logger.debug(f"복지로 JSON API 미응답(HTTP {response.status_code}), HTML 폴백 수집 진행 ({url})")
        except Exception as e:
            logger.debug(f"복지로 API 접속 예외 발생, HTML 폴백 수집 진행 ({url}): {str(e)}")
            items = []

        if items:
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
        else:
            # HTML / 서비스 목록 폴백 수집
            try:
                res = await client.get(url, timeout=settings.REQUEST_TIMEOUT)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "lxml")
                    # 복지로 메인안내 또는 소식 항목 수집
                    parsed_titles = set()
                    for elem in soup.find_all(["a", "div", "span"]):
                        txt = elem.get_text(strip=True)
                        if "복지" in txt and len(txt) > 10 and txt not in parsed_titles:
                            parsed_titles.add(txt)
                            if len(parsed_titles) > 5:
                                break
                    
                    target_type = "중앙 복지서비스" if tab_id == "1" else "지방 복지서비스"
                    base_title = f"[복지로] {publisher} {target_type} 안내"
                    articles.append(
                        Article(
                            id=f"bokjiro_fallback_{tab_id}",
                            title=base_title,
                            content=f"[{publisher}] 복지로 {target_type} 검색 및 신청 서비스 안내",
                            url=url,
                            site_name=publisher,
                            published_at=datetime.now(timezone.utc),
                            category=category,
                            extra_meta={
                                "portal_id": portal_id,
                                "tab_id": tab_id,
                                "purpose": source_cfg.get("purpose", []),
                            },
                        )
                    )
            except Exception as fe:
                logger.debug(f"복지로 폴백 수집 실패 ({url}): {str(fe)}")

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

    async def _parse_korea_kr(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """대한민국 정책브리핑(korea.kr) 정책뉴스 및 보도자료 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        publisher = source_cfg.get("publisher", "대한민국 정책브리핑")
        category = source_cfg.get("category", "정부정책")

        articles: List[Article] = []
        response = await client.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        seen_ids = set()
        view_pattern = re.compile(r"(policyNewsView|pressReleaseView)\.do")

        for a in soup.find_all("a", href=view_pattern):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if not title or len(title) < 3:
                continue

            id_match = re.search(r"newsId=(\d+)", href)
            news_id = id_match.group(1) if id_match else ""
            if news_id in seen_ids:
                continue
            if news_id:
                seen_ids.add(news_id)

            parent = a.find_parent("li") or a.find_parent("tr") or a.find_parent("div")
            date_str = None
            if parent:
                d_match = re.search(r"202\d[.-]\d{2}[.-]\d{2}", parent.get_text())
                if d_match:
                    date_str = d_match.group(0)

            pub_date = self._parse_date(date_str)

            if href.startswith("http"):
                detail_url = href
            else:
                detail_url = urljoin(url, href)

            article = Article(
                id=f"korea_{news_id or abs(hash(title))}",
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

    async def _parse_mohw(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """보건복지부(mohw.go.kr) 보도자료 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "")
        publisher = source_cfg.get("publisher", "보건복지부")
        category = source_cfg.get("category", "복지정책")

        articles: List[Article] = []
        response = await client.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        seen_ids = set()
        for tr in soup.select("table.tstyle_list tbody tr"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue

            a = tds[1].find("a")
            if not a:
                continue

            href = a.get("href", "")
            id_match = re.search(r"list_no=(\d+)", href)
            list_no = id_match.group(1) if id_match else ""

            # 새글 배지 등 태그 제거
            for badge in a.find_all(["span", "em", "i", "strong"]):
                badge.decompose()

            raw_title = a.get_text(strip=True)
            title = re.sub(r"^새글\s*", "", raw_title).strip()
            if not title:
                continue

            item_key = list_no or title
            if item_key in seen_ids:
                continue
            seen_ids.add(item_key)

            dept = tds[2].get_text(strip=True)
            date_str = tds[3].get_text(strip=True)
            pub_date = self._parse_date(date_str)

            detail_url = urljoin("https://www.mohw.go.kr", href) if href else url

            article = Article(
                id=f"mohw_{list_no or abs(hash(title))}",
                title=title,
                content=f"[{publisher}{' ' + dept if dept else ''}] {title}",
                url=detail_url,
                site_name=publisher,
                published_at=pub_date,
                category=category,
                extra_meta={
                    "portal_id": portal_id,
                    "department": dept,
                    "purpose": source_cfg.get("purpose", []),
                },
            )
            articles.append(article)

        return articles

    def _parse_blind_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """블라인드 작성시간 파싱 (상대시간 및 날짜)"""
        if not date_str:
            return None
        now = datetime.now(timezone.utc)
        clean_str = date_str.replace("작성시간", "").strip()
        if not clean_str:
            return now
        if "분" in clean_str:
            m = re.search(r"(\d+)\s*분", clean_str)
            mins = int(m.group(1)) if m else 0
            return now - timedelta(minutes=mins)
        if "시간" in clean_str:
            m = re.search(r"(\d+)\s*시간", clean_str)
            hrs = int(m.group(1)) if m else 0
            return now - timedelta(hours=hrs)
        if "어제" in clean_str:
            return now - timedelta(days=1)
        if "그저께" in clean_str or "2일 전" in clean_str:
            return now - timedelta(days=2)
        m_day = re.search(r"(\d+)\s*일", clean_str)
        if m_day:
            days = int(m_day.group(1))
            return now - timedelta(days=days)
        m_md = re.match(r"^(\d{1,2})\.(\d{1,2})\.?$", clean_str)
        if m_md:
            month, day = int(m_md.group(1)), int(m_md.group(2))
            return datetime(now.year, month, day, tzinfo=timezone.utc)
        m_ymd = re.match(r"^(\d{4})\.(\d{1,2})\.(\d{1,2})\.?$", clean_str)
        if m_ymd:
            y, m, d = int(m_ymd.group(1)), int(m_ymd.group(2)), int(m_ymd.group(3))
            return datetime(y, m, d, tzinfo=timezone.utc)
        return now

    async def _parse_teamblind(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """블라인드(teamblind.com) 토픽 및 베스트 게시글 수집 파서"""
        url = source_cfg.get("url", "")
        portal_id = source_cfg.get("id", "teamblind")
        publisher = source_cfg.get("publisher", "블라인드")
        category = source_cfg.get("category", "커뮤니티")
        target_count = source_cfg.get("target_count", 100)

        # 기본 토픽 URL 및 보조 검색 엔드포인트
        target_urls = [url]
        if portal_id == "teamblind_economy":
            target_urls.extend([
                "https://www.teamblind.com/kr/search/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC",
                "https://www.teamblind.com/kr/search/%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC",
                "https://www.teamblind.com/kr/search/%EA%B2%BD%EC%A0%9C",
            ])

        blind_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        articles: List[Article] = []
        seen_ids = set()

        for target_url in target_urls:
            if len(articles) >= target_count:
                break
            try:
                response = await client.get(
                    target_url,
                    headers=blind_headers,
                    timeout=settings.REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")

                for card in soup.select(".article-list-pre"):
                    if len(articles) >= target_count:
                        break

                    a_tit = card.select_one(".tit h3 a")
                    if not a_tit:
                        continue

                    href = a_tit.get("href", "")
                    if not href or "/kr/post/" not in href or "coupang.com" in href:
                        continue

                    for badge in a_tit.find_all(["span", "em", "i", "strong"]):
                        badge.decompose()

                    title = a_tit.get_text(strip=True)
                    if not title:
                        continue

                    alias_match = re.search(r"-([a-zA-Z0-9]+)$", href)
                    post_id = alias_match.group(1) if alias_match else href
                    if post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)

                    p_desc = card.select_one(".pre-txt a")
                    content_preview = " ".join(p_desc.get_text().split()) if p_desc else title

                    author_el = card.select_one(".sub p.name a")
                    author = " ".join(author_el.get_text().split()) if author_el else ""

                    date_el = card.select_one(".wrap-info a.past")
                    date_str = date_el.get_text(strip=True) if date_el else ""
                    pub_date = self._parse_blind_date(date_str)

                    cat_el = card.select_one(".category a.topic-name")
                    card_category = cat_el.get_text(strip=True) if cat_el else category

                    detail_url = urljoin("https://www.teamblind.com", href)

                    article = Article(
                        id=f"blind_{post_id}",
                        title=title,
                        content=f"[{author}] {content_preview}" if author else content_preview,
                        url=detail_url,
                        site_name=publisher,
                        published_at=pub_date,
                        category=card_category,
                        extra_meta={
                            "portal_id": portal_id,
                            "topic": card_category,
                            "author": author,
                            "raw_date": date_str,
                            "purpose": source_cfg.get("purpose", []),
                        },
                    )
                    articles.append(article)
            except Exception as e:
                logger.warning(f"블라인드 수집 중 오류 발생 ({target_url}): {e}")
                continue

        logger.info(f"[블라인드 - {portal_id}] 총 {len(articles)}개 게시글 수집 완료")
        return articles

    def _parse_fomos_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """포모스 등록일시 파싱 ('14:33', '09-13', 'YYYY-MM-DD')"""
        if not date_str:
            return None
        now = datetime.now(timezone.utc)
        clean_str = date_str.strip()
        if not clean_str:
            return now
        # 당일 시:분 (예: 14:33)
        if re.match(r"^\d{1,2}:\d{2}$", clean_str):
            h, m = map(int, clean_str.split(":"))
            return datetime(now.year, now.month, now.day, h, m, tzinfo=timezone.utc)
        # 당해 월-일 (예: 09-13)
        if re.match(r"^\d{1,2}-\d{1,2}$", clean_str):
            m, d = map(int, clean_str.split("-"))
            return datetime(now.year, m, d, tzinfo=timezone.utc)
        # 전체 년-월-일 (예: 2024-09-13)
        if re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", clean_str):
            y, m, d = map(int, clean_str.split("-"))
            return datetime(y, m, d, tzinfo=timezone.utc)
        return now

    async def _parse_fomos(
        self, source_cfg: dict, client: httpx.AsyncClient
    ) -> List[Article]:
        """
        포모스(fomos.kr) 가십 게시판 수집 파서:
        1. 가십 실시간 인기 (10개)
        2. 가십 주간 인기 (10개)
        3. 게시판 일반 목록 (최대 100개, page 페이징)
        """
        base_url = source_cfg.get("url", "https://www.fomos.kr/talk/article_list?bbs_id=4")
        portal_id = source_cfg.get("id", "fomos_talk_gossip")
        publisher = source_cfg.get("publisher", "포모스")
        category = source_cfg.get("category", "커뮤니티")
        target_count = source_cfg.get("target_count", 100)

        fomos_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        articles: List[Article] = []
        now = datetime.now(timezone.utc)

        first_page_url = base_url if "page=" in base_url else f"{base_url}&page=1"
        try:
            response = await client.get(first_page_url, headers=fomos_headers, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            logger.warning(f"포모스 1페이지 로드 실패 ({first_page_url}): {e}")
            return []

        # (1) 가십 실시간 인기 (10개)
        box_left = soup.select_one(".postbox.left")
        if box_left:
            for a in box_left.find_all("a"):
                href = a.get("href", "")
                raw_title = a.get_text(strip=True)
                title = re.sub(r"\(\d+\)$", "", raw_title).strip()
                if not title:
                    continue
                idx_match = re.search(r"indexno=(\d+)", href)
                idx = idx_match.group(1) if idx_match else abs(hash(title))
                detail_url = f"https://www.fomos.kr/talk/article_view?bbs_id=4&indexno={idx}"
                article = Article(
                    id=f"fomos_popular_realtime_{idx}",
                    title=f"[실시간 인기] {title}",
                    content=f"[{publisher} 가십 실시간 인기] {title}",
                    url=f"{detail_url}#realtime",
                    site_name=publisher,
                    published_at=now,
                    category=category,
                    extra_meta={
                        "portal_id": portal_id,
                        "section": "realtime_popular",
                        "purpose": source_cfg.get("purpose", []),
                    },
                )
                articles.append(article)

        # (2) 가십 주간 인기 (10개)
        box_right = soup.select_one(".postbox.right")
        if box_right:
            for a in box_right.find_all("a"):
                href = a.get("href", "")
                raw_title = a.get_text(strip=True)
                title = re.sub(r"\(\d+\)$", "", raw_title).strip()
                if not title:
                    continue
                idx_match = re.search(r"indexno=(\d+)", href)
                idx = idx_match.group(1) if idx_match else abs(hash(title))
                detail_url = f"https://www.fomos.kr/talk/article_view?bbs_id=4&indexno={idx}"
                article = Article(
                    id=f"fomos_popular_weekly_{idx}",
                    title=f"[주간 인기] {title}",
                    content=f"[{publisher} 가십 주간 인기] {title}",
                    url=f"{detail_url}#weekly",
                    site_name=publisher,
                    published_at=now,
                    category=category,
                    extra_meta={
                        "portal_id": portal_id,
                        "section": "weekly_popular",
                        "purpose": source_cfg.get("purpose", []),
                    },
                )
                articles.append(article)

        # (3) 게시판 일반 목록 수집 (target_count 기본 100개 목표)
        board_count = 0
        current_page = 1
        current_soup = soup

        while board_count < target_count and current_page <= 10:
            if current_page > 1:
                page_url = f"https://www.fomos.kr/talk/article_list?bbs_id=4&page={current_page}"
                try:
                    await asyncio.sleep(0.3)
                    p_resp = await client.get(page_url, headers=fomos_headers, timeout=settings.REQUEST_TIMEOUT)
                    p_resp.raise_for_status()
                    current_soup = BeautifulSoup(p_resp.text, "lxml")
                except Exception as e:
                    logger.warning(f"포모스 {current_page}페이지 로드 실패: {e}")
                    break

            table = current_soup.select_one("table.board_list")
            if not table:
                break

            rows = table.find_all("tr")[1:]  # 헤더 제외
            for row in rows:
                if board_count >= target_count:
                    break
                tds = row.find_all("td")
                if len(tds) < 5:
                    continue
                num_str = tds[0].get_text(strip=True)
                if num_str == "공지":
                    continue

                a_tag = tds[1].find("a")
                if not a_tag:
                    continue

                href = a_tag.get("href", "")
                raw_title = a_tag.get_text(strip=True)
                title = re.sub(r"\[\d+\]$", "", raw_title).strip()
                if not title:
                    continue

                author = tds[2].get_text(strip=True)
                date_str = tds[3].get_text(strip=True)
                pub_date = self._parse_fomos_date(date_str)
                views = tds[4].get_text(strip=True)
                likes = tds[5].get_text(strip=True) if len(tds) > 5 else "0"

                idx_match = re.search(r"indexno=(\d+)", href)
                idx = idx_match.group(1) if idx_match else num_str
                detail_url = f"https://www.fomos.kr/talk/article_view?bbs_id=4&indexno={idx}"

                article = Article(
                    id=f"fomos_{idx}",
                    title=title,
                    content=f"[{author}] {title} (조회 {views}, 공감 {likes})",
                    url=detail_url,
                    site_name=publisher,
                    published_at=pub_date,
                    category=category,
                    extra_meta={
                        "portal_id": portal_id,
                        "section": "board",
                        "author": author,
                        "raw_date": date_str,
                        "views": views,
                        "likes": likes,
                        "purpose": source_cfg.get("purpose", []),
                    },
                )
                articles.append(article)
                board_count += 1

            current_page += 1

        realtime_cnt = len(box_left.find_all("a")) if box_left else 0
        weekly_cnt = len(box_right.find_all("a")) if box_right else 0
        logger.info(f"[포모스] 실시간 {realtime_cnt}개 + 주간 {weekly_cnt}개 + 게시판 {board_count}개 = 총 {len(articles)}개 수집 완료")
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
            if "fomos" in portal_id or "fomos.kr" in url:
                return await self._parse_fomos(source_cfg, client)
            elif "teamblind" in portal_id or "teamblind.com" in url:
                return await self._parse_teamblind(source_cfg, client)
            elif "korea" in portal_id or "korea.kr" in url:
                return await self._parse_korea_kr(source_cfg, client)
            elif "mohw" in portal_id or "mohw.go.kr" in url:
                return await self._parse_mohw(source_cfg, client)
            elif "gov24" in portal_id or "gov.kr" in url:
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

