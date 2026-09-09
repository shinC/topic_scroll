import hashlib
from typing import List, Set
from models.article import Article
from utils.logger import logger


class ArticleProcessor:
    """
    수집된 기사 데이터를 정제하고 중복을 제거하는 처리기
    """

    def __init__(self):
        self._seen_urls: Set[str] = set()
        self._seen_hashes: Set[str] = set()

    def generate_hash(self, article: Article) -> str:
        """기사 제목과 URL을 기반으로 unique MD5 해시값을 생성합니다."""
        raw_key = f"{article.url}_{article.title}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def process(self, articles: List[Article]) -> List[Article]:
        """
        기사 목록에서 중복 기사를 제거하고 데이터 필드를 정지/보정합니다.
        """
        processed_articles: List[Article] = []

        for article in articles:
            # 1. URL 중복 체크
            if article.url in self._seen_urls:
                logger.debug(f"중복 기사 제외 (URL): {article.url}")
                continue

            # 2. 해시 중복 체크 및 ID 부여
            art_hash = self.generate_hash(article)
            if art_hash in self._seen_hashes:
                logger.debug(f"중복 기사 제외 (해시): {article.title}")
                continue

            if not article.id:
                article.id = f"art_{art_hash[:12]}"

            # 3. 텍스트 트림 정제
            article.title = article.title.strip()
            article.content = article.content.strip()

            self._seen_urls.add(article.url)
            self._seen_hashes.add(art_hash)
            processed_articles.append(article)

        logger.info(
            f"데이터 전처리 완료: 원본 {len(articles)}개 -> 중복 제거 후 {len(processed_articles)}개"
        )
        return processed_articles
