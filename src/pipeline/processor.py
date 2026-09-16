import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Set
from models.article import Article
from utils.logger import logger


class ArticleProcessor:
    """
    수집된 기사 데이터를 정제하고 중복을 제거하며, 5일 이상 지난 데이터를 필터링하는 처리기
    """

    def __init__(self, max_age_days: int = 5):
        self._seen_urls: Set[str] = set()
        self._seen_hashes: Set[str] = set()
        self.max_age_days = max_age_days
        # 키워드 매칭 설정 로드
        self._load_keywords()



    def _load_keywords(self) -> None:
        """keywords.yaml에서 카테고리별 키워드 매핑 테이블을 생성합니다."""
        try:
            from config import load_keywords_config
            kw_config = load_keywords_config()
            self._categories = kw_config.get("categories", {})
        except Exception as e:
            logger.warning(f"키워드 설정 로드 실패: {str(e)}")
            self._categories = {}

    def extract_tags_and_category(self, article: Article) -> tuple[List[str], Optional[str]]:
        """기사 제목과 본문을 기반으로 카테고리 및 태그 키워드를 추출합니다."""
        matched_tags: List[str] = []
        matched_categories: List[str] = []
        target_text = f"{article.title} {article.summary or ''} {article.content or ''}".lower()

        for cat_key, cat_data in self._categories.items():
            cat_name = cat_data.get("name", cat_key)
            keywords_group = cat_data.get("keywords", {})

            for sub_group, kw_list in keywords_group.items():
                if isinstance(kw_list, list):
                    for kw in kw_list:
                        if kw.lower() in target_text:
                            if kw not in matched_tags:
                                matched_tags.append(kw)
                            if cat_name not in matched_categories:
                                matched_categories.append(cat_name)

        # 주 카테고리 설정 (기존 지정 카테고리가 없거나 매칭된 것이 있으면 적용)
        category = article.category
        if matched_categories:
            category = matched_categories[0]

        return matched_tags, category

    def generate_hash(self, article: Article) -> str:
        """기사 제목과 URL을 기반으로 unique MD5 해시값을 생성합니다."""
        raw_key = f"{article.url}_{article.title}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def process(self, articles: List[Article]) -> List[Article]:
        """
        기사 목록에서 중복 기사를 제거하고, 5일 이상 지난 기사를 제외하며 데이터 필드를 정제합니다.
        """
        processed_articles: List[Article] = []
        now = datetime.now(timezone.utc)

        for article in articles:
            # 0. 5일 이상 차이나는 오래된 기사 제외 (published_at 기준)
            if article.published_at:
                pub_at = article.published_at
                if pub_at.tzinfo is None:
                    pub_at = pub_at.replace(tzinfo=timezone.utc)
                age_days = (now - pub_at).total_seconds() / 86400.0
                if age_days >= self.max_age_days:
                    logger.info(
                        f"5일 이상 경과 기사 제외 ({pub_at.strftime('%Y-%m-%d')}, {age_days:.1f}일 경과): {article.title}"
                    )
                    continue

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

            # 4. 키워드 태그 및 카테고리 자동 자동 추출
            tags, category = self.extract_tags_and_category(article)
            if tags:
                article.tags = tags
            if category:
                article.category = category

            self._seen_urls.add(article.url)
            self._seen_hashes.add(art_hash)
            processed_articles.append(article)

        logger.info(
            f"데이터 전처리 완료: 원본 {len(articles)}개 -> 중복 제거 후 {len(processed_articles)}개"
        )
        return processed_articles

