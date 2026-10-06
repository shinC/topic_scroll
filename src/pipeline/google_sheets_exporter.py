from datetime import datetime
from typing import List
import gspread
from google.oauth2.service_account import Credentials

from config import settings
from models.article import Article, ScrapingResult
from utils.logger import logger

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


from bs4 import BeautifulSoup


def _clean_body_text(text: str) -> str:
    """본문 텍스트에서 HTML 태그를 제거하고 공백을 정제하여 초반 300자 반환"""
    if not text:
        return ""
    if "<" in text and ">" in text:
        try:
            text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
        except Exception:
            pass
    cleaned = " ".join(text.split())
    return cleaned[:300]


def _get_article_priority(article: Article) -> int:
    """
    구글 시트 출력 순서 우선순위 계산:
    1: 커뮤니티 (포모스, 블라인드) - 최상위
    2: 언론사 RSS 뉴스 - 중간
    3: 정부 정책 및 공공 포털 - 가장 하단
    """
    portal_id = str(article.extra_meta.get("portal_id", "")).lower()
    art_id = str(article.id or "").lower()
    site_name = str(article.site_name or "").lower()

    # 1. 포모스 & 블라인드 (최상위)
    if (
        "fomos" in portal_id
        or "blind" in portal_id
        or "fomos" in art_id
        or "blind" in art_id
        or "포모스" in site_name
        or "블라인드" in site_name
    ):
        return 1

    # 3. 정부 정책 / 공공 포털 (가장 하단)
    govt_keywords = [
        "gov24",
        "work24",
        "bokjiro",
        "molit",
        "korea",
        "mohw",
        "정부",
        "고용24",
        "복지로",
        "국토",
        "정책브리핑",
        "보건복지부",
        "행정안전부",
    ]
    if (
        any(k in portal_id for k in ["gov24", "work24", "bokjiro", "molit", "korea", "mohw"])
        or any(k in art_id for k in ["gov24_", "work24_", "bokjiro_", "molit_", "korea_", "mohw_"])
        or any(k in site_name for k in govt_keywords)
    ):
        return 3

    # 2. 일반 RSS 뉴스 (중간)
    return 2


class GoogleSheetsExporter:
    """
    수집된 뉴스/포털 데이터를 구글 스프레드시트에 저장하는 엑스포터
    사용자 요청에 따라 실행 시마다 기존 시트 내용을 덮어쓰는(Overwrite) 방식으로 동작합니다.
    """

    def __init__(
        self,
        service_account_file=settings.GOOGLE_SERVICE_ACCOUNT_FILE,
        spreadsheet_id: str = settings.GOOGLE_SPREADSHEET_ID,
    ):
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self._client = None
        self._spreadsheet = None

    def _connect(self):
        """gspread 구글 클라이언트를 인증하고 연결합니다."""
        if self._client is None:
            if not self.service_account_file.exists():
                raise FileNotFoundError(
                    f"구글 서비스 계정 키 파일을 찾을 수 없습니다: {self.service_account_file}"
                )
            creds = Credentials.from_service_account_file(
                str(self.service_account_file), scopes=SCOPES
            )
            self._client = gspread.authorize(creds)
            self._spreadsheet = self._client.open_by_key(self.spreadsheet_id)

    def export(self, articles: List[Article], sheet_name: str = "Sheet1") -> bool:
        """
        수집된 기사 리스트를 구글 스프레드시트에 덮어씁니다.
        사용자 요청에 따라:
        1. 최상위: 포모스, 블라인드 커뮤니티 글
        2. 중간: RSS 뉴스
        3. 가장 하단: 정부 정책 및 공공 포털
        """
        if not articles:
            logger.warning("구글 스프레드시트에 저장할 기사 데이터가 없습니다.")
            return False

        try:
            self._connect()

            # 워크시트 가져오기 (없으면 첫 번째 워크시트 사용)
            try:
                sheet = self._spreadsheet.worksheet(sheet_name)
            except Exception:
                sheet = self._spreadsheet.get_worksheet(0)

            # 사용자 요청에 따른 정렬 (1: 포모스/블라인드 -> 2: RSS뉴스 -> 3: 정부정책)
            sorted_articles = sorted(
                articles,
                key=lambda a: (
                    _get_article_priority(a),
                    -(a.published_at.timestamp() if a.published_at else 0),
                ),
            )

            logger.info(
                f"[Google Sheets] '{sheet.title}' 시트 데이터를 덮어쓰는 중... (총 {len(sorted_articles)}건, 포모스/블라인드 상단 배치)"
            )

            # 사용자 요청: 실행할 때마다 덮어쓰는 방식 -> clear()
            sheet.clear()

            # 헤더 행 작성
            headers = [
                "수집일시",
                "발행일시",
                "출처",
                "카테고리",
                "제목",
                "본문 (초반 300자)",
                "링크",
                "관련 태그",
            ]

            rows = [headers]
            for idx, article in enumerate(sorted_articles, start=1):
                scraped_str = (
                    article.scraped_at.strftime("%Y-%m-%d %H:%M:%S")
                    if article.scraped_at
                    else ""
                )
                published_str = (
                    article.published_at.strftime("%Y-%m-%d %H:%M:%S")
                    if article.published_at
                    else ""
                )
                tags_str = ", ".join(article.tags) if article.tags else ""
                body_text = _clean_body_text(article.content or article.summary or article.title)

                row = [
                    scraped_str,
                    published_str,
                    article.site_name,
                    article.category or "",
                    article.title,
                    body_text,
                    article.url,
                    tags_str,
                ]
                rows.append(row)

                # 사용자 요청: 20개 단위로 분할하여 빈 행(빈칸) 삽입 (마지막 기사 이후는 제외)
                if idx % 20 == 0 and idx < len(articles):
                    rows.append([""] * len(headers))

            # 한 번에 모든 행 업데이트
            sheet.update(range_name="A1", values=rows)

            logger.info(
                f"[Google Sheets] 성공적으로 {len(articles)}개 기사를 구글 스프레드시트에 내보냈습니다!"
            )
            return True

        except Exception as e:
            logger.error(f"[Google Sheets] 스프레드시트 내보내기 실패: {str(e)}")
            return False
