import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List
from config import settings
from models.article import Article, ScrapingResult
from utils.logger import logger


class ArticleExporter:
    """
    수집된 기사 데이터를 파일(JSON, JSONL, CSV)로 내보내는 엑스포터
    """

    def __init__(self, output_dir: Path = settings.DATA_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_result(self, result: ScrapingResult, format_type: str = settings.EXPORT_FORMAT) -> Path:
        """
        ScrapingResult 전체 결과를 파일로 저장합니다.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_site_name = result.site_name.replace(" ", "_").lower()

        if format_type == "jsonl":
            filename = f"{safe_site_name}_{timestamp}.jsonl"
            file_path = self.output_dir / filename
            self.to_jsonl(result.articles, file_path)
        elif format_type == "csv":
            filename = f"{safe_site_name}_{timestamp}.csv"
            file_path = self.output_dir / filename
            self.to_csv(result.articles, file_path)
        else:  # 기본 json
            filename = f"{safe_site_name}_{timestamp}.json"
            file_path = self.output_dir / filename
            self.to_json(result, file_path)

        logger.info(f"결과 저장 완료: {file_path}")
        return file_path

    def to_json(self, result: ScrapingResult, file_path: Path) -> None:
        """JSON 포맷으로 저장합니다."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    def to_jsonl(self, articles: List[Article], file_path: Path) -> None:
        """JSON Lines 포맷으로 기사를 1줄씩 저장합니다."""
        with open(file_path, "w", encoding="utf-8") as f:
            for article in articles:
                f.write(json.dumps(article.model_dump(mode="json"), ensure_ascii=False) + "\n")

    def to_csv(self, articles: List[Article], file_path: Path) -> None:
        """CSV 포맷으로 저장합니다."""
        if not articles:
            logger.warning("저장할 기사가 없습니다. 빈 CSV 파일을 생성합니다.")
            return

        fieldnames = ["id", "site_name", "title", "url", "author", "published_at", "scraped_at", "category", "summary"]
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for article in articles:
                writer.writerow(article.model_dump(mode="json"))
