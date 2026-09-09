import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    프로젝트 주요 설정 관리 클래스
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 기본 프로젝트 경로
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # 앱 실행 환경 설정
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # 수집 결과 데이터 저장 설정
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    EXPORT_FORMAT: str = "json"  # json, jsonl, csv

    # 네트워크 / HTTP 요청 설정
    REQUEST_TIMEOUT: float = 15.0
    MAX_CONCURRENT_REQUESTS: int = 5
    DEFAULT_USER_AGENT: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    )

    # 구글 스프레드시트 연동 설정
    GOOGLE_SERVICE_ACCOUNT_FILE: Path = BASE_DIR / "key" / "topic-scroll-f2585775b967.json"
    GOOGLE_SPREADSHEET_ID: str = "1oTLOAohWi3PXQVTvWcY8wTJe-OX3Iz2v400BNUBuJDA"

    # 설정 파일 경로
    CONFIG_DIR: Path = BASE_DIR / "src" / "config"

    def setup_directories(self) -> None:
        """필요한 디렉터리(data, logs)가 없으면 생성합니다."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


# 싱글톤 설정 객체 생성
settings = Settings()
settings.setup_directories()


def load_yaml_config(filename: str) -> dict:
    """src/config 디렉터리 내 YAML 파일을 로드합니다."""
    import yaml
    filepath = settings.CONFIG_DIR / filename
    if not filepath.exists():
        # 루트 /app/src/config 대신 다른 경로 시도
        alt_filepath = Path(__file__).resolve().parent / "config" / filename
        if alt_filepath.exists():
            filepath = alt_filepath
        else:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {filename}")

    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_feeds_config() -> dict:
    return load_yaml_config("feeds.yaml")


def load_keywords_config() -> dict:
    return load_yaml_config("keywords.yaml")


def load_portal_config() -> dict:
    return load_yaml_config("portal.yaml")

