# topic_scroll 개발자 가이드 📘

본 문서는 `topic_scroll` 프로젝트에 새로운 뉴스 사이트 스크래퍼 모듈을 추가하는 방법에 대한 개발 가이드입니다.

---

## 스크래퍼 개발 단계 Overview

`topic_scroll`은 레지스트리 기반의 모듈형 구조로 되어 있어서, 신규 사이트 수집기를 개발할 때 기존 코드를 수정할 필요 없이 파일 하나만 추가하면 자동으로 인식되어 실행됩니다.

전체 구현 순서:
1. `src/scrapers/implementations/` 아래에 새로운 `.py` 파일 생성
2. `BaseScraper` 클래스 상속 및 `@scraper_registry.register` 데코레이터 적용
3. 필수 프로퍼티 및 `parse()` 비동기 메서드 구현
4. 실행 및 동작 테스트

---

## 단계별 상세 구현 방법

### 1. 스크래퍼 파일 생성

예를 들어 **연합뉴스(Yonhap News)** 수집기를 새로 만든다면, `src/scrapers/implementations/yonhap_news.py` 파일을 생성합니다.

### 2. 코드 기본 템플릿 작성

```python
from typing import List
from bs4 import BeautifulSoup

from models.article import Article
from scrapers.base import BaseScraper
from scrapers.registry import scraper_registry
from utils.logger import logger


@scraper_registry.register
class YonhapNewsScraper(BaseScraper):
    """
    연합뉴스 기사 수집 스크래퍼
    """

    @property
    def name(self) -> str:
        """CLI 및 명령어로 지정할 고유 ID 이름 (소문자, 언더바)"""
        return "yonhap_news"

    @property
    def site_name(self) -> str:
        """화면에 표시될 언론사 / 사이트명"""
        return "연합뉴스"

    @property
    def base_url(self) -> str:
        """수집 대상 메인 / 섹션 URL"""
        return "https://www.yna.co.kr/news"

    async def parse(self, html: str, url: str) -> List[Article]:
        """
        HTML 텍스트에서 기사 요소를 추출하여 Article 객체 리스트로 반환합니다.
        """
        soup = BeautifulSoup(html, "lxml")
        articles: List[Article] = []

        # 뉴스 리스트 요소 선택
        news_items = soup.select("div.news-con")

        for item in news_items:
            try:
                title_elem = item.select_one("a.tit")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                article_url = title_elem.get("href", "")
                if article_url.startswith("//"):
                    article_url = f"https:{article_url}"

                # Article 데이터 모델 생성
                article = Article(
                    title=title,
                    content=title, # 상세 페이지 수집 시 본문으로 교체 가능
                    url=article_url,
                    site_name=self.site_name,
                    category="주요뉴스"
                )
                articles.append(article)

            except Exception as e:
                logger.warning(f"연합뉴스 항목 파싱 중 예외: {str(e)}")
                continue

        return articles
```

---

## `Article` 데이터 모델 상세 필드

| 필드명 | 타입 | 설명 | 필수 여부 |
| :--- | :--- | :--- | :--- |
| `title` | `str` | 기사 제목 | 필수 |
| `content` | `str` | 기사 본문 텍스트 | 필수 |
| `url` | `str` | 기사 원본 링크 URL | 필수 |
| `site_name` | `str` | 출처 언론사명 | 필수 |
| `id` | `Optional[str]` | 기사 고유 식별자 (미입력 시 해시값 자동 생성) | 선택 |
| `author` | `Optional[str]` | 작성자 / 기자 이름 | 선택 |
| `published_at` | `Optional[datetime]` | 기사 작성일시 | 선택 |
| `category` | `Optional[str]` | 기사 카테고리 (정치, 경제 등) | 선택 |
| `summary` | `Optional[str]` | 기사 요약 문구 | 선택 |
| `tags` | `List[str]` | 관련 키워드 태그 리스트 | 선택 |
| `extra_meta` | `Dict[str, Any]` | 기타 언론사 특화 메타데이터 | 선택 |

---

## 3. 동적 상세 페이지 수집 (필요 시)

목록 페이지뿐만 아니라 각 기사 URL로 들어가 본문 전체를 상세 수집해야 하는 경우 `self.fetch_page()`를 사용할 수 있습니다.

```python
async def parse(self, html: str, url: str) -> List[Article]:
    soup = BeautifulSoup(html, "lxml")
    articles: List[Article] = []

    for item in soup.select("ul.news_list > li"):
        link_elem = item.select_one("a")
        if not link_elem:
            continue
        
        detail_url = link_elem["href"]
        
        # 비동기로 상세 페이지 HTML 가져오기
        try:
            detail_html = await self.fetch_page(detail_url)
            detail_soup = BeautifulSoup(detail_html, "lxml")
            
            title = detail_soup.select_one("h1.title").get_text(strip=True)
            body = detail_soup.select_one("article.body").get_text(strip=True)
            
            articles.append(Article(
                title=title,
                content=body,
                url=detail_url,
                site_name=self.site_name
            ))
        except Exception as e:
            logger.error(f"상세 페이지 수집 실패 ({detail_url}): {e}")

    return articles
```

---

## 4. 테스트 방법

새로 만든 스크래퍼가 정상 등록되었는지 테스트합니다.

```bash
# 1. 스크래퍼 목록에 새로 만든 스크래퍼가 뜨는지 확인
python src/main.py list

# 2. 새로 만든 스크래퍼만 단독 실행 테스트
python src/main.py run yonhap_news

# 3. 도커 환경에서 테스트
docker compose run --rm app run yonhap_news
```
