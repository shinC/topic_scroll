from typing import List
from bs4 import BeautifulSoup
from models.article import Article
from scrapers.base import BaseScraper
from scrapers.registry import scraper_registry
from utils.logger import logger


@scraper_registry.register
class SampleNewsScraper(BaseScraper):
    """
    해커뉴스(Hacker News) 기반 샘플 뉴스 스크래퍼 예시 구현체
    """

    @property
    def name(self) -> str:
        return "sample_news"

    @property
    def site_name(self) -> str:
        return "샘플 해커뉴스"

    @property
    def base_url(self) -> str:
        return "https://news.ycombinator.com"

    async def parse(self, html: str, url: str) -> List[Article]:
        """
        해커뉴스 메인 페이지 HTML을 파싱하여 기사 목록을 가져옵니다.
        """
        soup = BeautifulSoup(html, "lxml")
        articles: List[Article] = []

        # 해커뉴스 기사 행 태그 (.athing)
        title_rows = soup.select("tr.athing")
        
        for row in title_rows:
            try:
                story_id = row.get("id", "")
                title_elem = row.select_one("span.titleline > a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                article_url = title_elem.get("href", "")
                
                # 상대 경로 URL 인 경우 기본 URL 결합
                if article_url.startswith("item?id="):
                    article_url = f"{self.base_url}/{article_url}"

                # 다음 행에서 메타 정보 추출 (작성자, 점수 등)
                subtext = row.find_next_sibling("tr")
                author = None
                if subtext:
                    author_elem = subtext.select_one("a.hnuser")
                    if author_elem:
                        author = author_elem.get_text(strip=True)

                article = Article(
                    id=f"hn_{story_id}" if story_id else None,
                    title=title,
                    content=f"해커뉴스 링크 기사: {title}",
                    url=article_url,
                    site_name=self.site_name,
                    author=author,
                    category="IT/기술",
                    extra_meta={"story_id": story_id}
                )
                articles.append(article)
            except Exception as e:
                logger.warning(f"기사 파싱 실패 (행 분석 오류): {str(e)}")
                continue

        return articles
