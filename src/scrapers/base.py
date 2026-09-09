import time
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup

from models.article import Article, ScrapingResult
from utils.http_client import get_http_client, fetch_html
from utils.logger import logger


class BaseScraper(ABC):
    """
    모든 뉴스 사이트 스크래퍼가 상속받는 추상 클래스 (Base Scraper)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """스크래퍼 고유 식별 이름 (예: 'sample_news', 'yonhap_news')"""
        pass

    @property
    @abstractmethod
    def site_name(self) -> str:
        """언론사 / 사이트명 (예: '샘플 뉴스', '연합뉴스')"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """대상 사이트의 기본 URL"""
        pass

    async def fetch_page(self, url: str, client: Optional[httpx.AsyncClient] = None) -> str:
        """페이지 HTML을 수집합니다."""
        return await fetch_html(url, client=client)

    @abstractmethod
    async def parse(self, html: str, url: str) -> List[Article]:
        """
        HTML 텍스트를 파싱하여 Article 객체 리스트를 생성합니다.
        
        Args:
            html: 웹페이지 HTML 소스
            url: 수집 대상 URL
        
        Returns:
            수집된 Article 객체 리스트
        """
        pass

    async def run(self, client: Optional[httpx.AsyncClient] = None) -> ScrapingResult:
        """
        수집 프로세스를 실행하고 ScrapingResult를 반환합니다.
        """
        start_time = time.time()
        logger.info(f"[{self.site_name}] 뉴스 수집 시작...")
        
        try:
            html = await self.fetch_page(self.base_url, client=client)
            articles = await self.parse(html, self.base_url)
            elapsed = time.time() - start_time
            
            logger.info(
                f"[{self.site_name}] 수집 완료: 총 {len(articles)}개 기사 "
                f"({elapsed:.2f}초 소요)"
            )
            return ScrapingResult(
                site_name=self.site_name,
                success=True,
                articles=articles,
                total_count=len(articles),
                execution_time_seconds=round(elapsed, 2)
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[{self.site_name}] 수집 중 오류 발생: {str(e)}")
            return ScrapingResult(
                site_name=self.site_name,
                success=False,
                articles=[],
                total_count=0,
                error_message=str(e),
                execution_time_seconds=round(elapsed, 2)
            )
