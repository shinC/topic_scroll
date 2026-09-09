from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    """
    수집된 뉴스 기사의 표준 데이터 모델
    """
    id: Optional[str] = Field(None, description="기사 고유 식별자 (해시 또는 URL 기반)")
    title: str = Field(..., description="기사 제목")
    content: str = Field(..., description="기사 본문 텍스트")
    url: str = Field(..., description="기사 원본 URL")
    site_name: str = Field(..., description="언론사 / 출처 사이트 이름")
    author: Optional[str] = Field(None, description="작성자 / 기자 이름")
    published_at: Optional[datetime] = Field(None, description="기사 발행 일시")
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="수집 처리 일시 (UTC)"
    )
    category: Optional[str] = Field(None, description="기사 카테고리 (정치, 경제, IT 등)")
    summary: Optional[str] = Field(None, description="기사 요약")
    tags: List[str] = Field(default_factory=list, description="관련 태그 키워드 목록")
    raw_html: Optional[str] = Field(None, description="원본 HTML (필요 시 포함)")
    extra_meta: Dict[str, Any] = Field(
        default_factory=dict,
        description="추가 확장 메타데이터"
    )


class ScrapingResult(BaseModel):
    """
    특정 뉴스 사이트 수집 작업 전체 결과 모델
    """
    site_name: str = Field(..., description="수집 대상 사이트명")
    success: bool = Field(..., description="수집 성공 여부")
    articles: List[Article] = Field(default_factory=list, description="수집된 기사 리스트")
    total_count: int = Field(0, description="수집 성공 기사 수")
    error_message: Optional[str] = Field(None, description="에러 발생 시 메세지")
    execution_time_seconds: float = Field(0.0, description="소요 시간(초)")
