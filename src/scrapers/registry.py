import importlib
import pkgutil
from typing import Dict, List, Type
from scrapers.base import BaseScraper
from utils.logger import logger


class ScraperRegistry:
    """
    사이트별 스크래퍼 모듈을 등록하고 관리하는 레지스트리 클래스
    """

    def __init__(self):
        self._scrapers: Dict[str, Type[BaseScraper]] = {}

    def register(self, scraper_cls: Type[BaseScraper]) -> Type[BaseScraper]:
        """
        스크래퍼 클래스를 레지스트리에 등록합니다 (데코레이터로도 활용 가능).
        """
        instance = scraper_cls()
        name = instance.name
        if name in self._scrapers:
            logger.warning(f"이미 등록된 스크래퍼 이름입니다: {name}. 덮어씁니다.")
        self._scrapers[name] = scraper_cls
        logger.debug(f"스크래퍼 등록 완료: {name} ({instance.site_name})")
        return scraper_cls

    def get_scraper(self, name: str) -> BaseScraper:
        """이름으로 등록된 스크래퍼 인스턴스를 반환합니다."""
        if name not in self._scrapers:
            raise KeyError(f"등록되지 않은 스크래퍼입니다: {name}")
        return self._scrapers[name]()

    def list_scrapers(self) -> List[str]:
        """등록된 전체 스크래퍼 이름 목록을 반환합니다."""
        return list(self._scrapers.keys())

    def get_all_scrapers(self) -> List[BaseScraper]:
        """등록된 모든 스크래퍼의 인스턴스 리스트를 반환합니다."""
        return [cls() for cls in self._scrapers.values()]

    def auto_discover(self) -> None:
        """
        scrapers.implementations 패키지 내의 모든 모듈을 자동으로 로드하여 스크래퍼를 등록합니다.
        """
        import scrapers.implementations as impl_pkg
        for _, module_name, _ in pkgutil.iter_modules(impl_pkg.__path__):
            full_module_name = f"scrapers.implementations.{module_name}"
            try:
                importlib.import_module(full_module_name)
                logger.debug(f"스크래퍼 모듈 로드 성공: {full_module_name}")
            except Exception as e:
                logger.error(f"모듈 로드 실패 ({full_module_name}): {str(e)}")


# 전역 스크래퍼 레지스트리 인스턴스
scraper_registry = ScraperRegistry()
