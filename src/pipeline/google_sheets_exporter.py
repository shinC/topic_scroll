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

            logger.info(
                f"[Google Sheets] '{sheet.title}' 시트 데이터를 덮어쓰는 중... (총 {len(articles)}건)"
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
                "링크",
                "관련 태그",
            ]

            rows = [headers]
            for article in articles:
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

                row = [
                    scraped_str,
                    published_str,
                    article.site_name,
                    article.category or "",
                    article.title,
                    article.url,
                    tags_str,
                ]
                rows.append(row)

            # 한 번에 모든 행 업데이트
            sheet.update(range_name="A1", values=rows)

            logger.info(
                f"[Google Sheets] 성공적으로 {len(articles)}개 기사를 구글 스프레드시트에 내보냈습니다!"
            )
            return True

        except Exception as e:
            logger.error(f"[Google Sheets] 스프레드시트 내보내기 실패: {str(e)}")
            return False
