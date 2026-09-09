import sys
from loguru import logger
from config import settings


def configure_logger():
    """
    Loguru 로깅을 한국어 메시지 및 파일/콘솔 출력에 맞게 설정합니다.
    """
    logger.remove()

    # 콘솔 출력 포맷
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:10}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # 파일 출력 포맷 (일자별 순환 로그)
    log_file_path = settings.LOGS_DIR / "topic_scroll_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_file_path),
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:10} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
    )

    return logger


# 싱글톤 로거 객체
logger = configure_logger()
