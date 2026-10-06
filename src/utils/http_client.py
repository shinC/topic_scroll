import asyncio
import httpx
from typing import Optional, Dict
from config import settings
from utils.logger import logger


def get_default_headers(custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    기본 HTTP 요청 헤더를 생성합니다.
    """
    headers = {
        "User-Agent": settings.DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if custom_headers:
        headers.update(custom_headers)
    return headers


def get_http_client(custom_headers: Optional[Dict[str, str]] = None) -> httpx.AsyncClient:
    """
    설정이 반영된 비동기 httpx.AsyncClient 인스턴스를 반환합니다.
    """
    return httpx.AsyncClient(
        headers=get_default_headers(custom_headers),
        timeout=httpx.Timeout(settings.REQUEST_TIMEOUT),
        follow_redirects=True,
    )


async def fetch_html(
    url: str,
    client: Optional[httpx.AsyncClient] = None,
    headers: Optional[Dict[str, str]] = None
) -> str:
    """
    지정된 URL에 비동기 GET 요청을 보내고 HTML 본문 텍스트를 반환합니다.
    """
    should_close = False
    if client is None:
        client = get_http_client(headers)
        should_close = True

    try:
        logger.debug(f"HTTP 요청 시작: {url}")
        response = await client.get(url, headers=get_default_headers(headers))
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            logger.debug(f"HTTP 403 발생으로 curl_cffi 브라우저 임퍼소네이션 재시도: {url}")
            try:
                from curl_cffi import requests as curl_requests
                resp = await asyncio.to_thread(
                    curl_requests.get,
                    url,
                    headers=get_default_headers(headers),
                    impersonate="chrome",
                    timeout=int(settings.REQUEST_TIMEOUT),
                )
                if resp.status_code == 200:
                    return resp.text
            except Exception as cf_err:
                logger.warning(f"curl_cffi 재시도 실패: {url} - {str(cf_err)}")
        logger.error(f"HTTP 오류 발생 [{e.response.status_code}] URL: {url}")
        raise
    except httpx.RequestError as e:
        logger.error(f"요청 실패: {url} - {str(e)}")
        raise
    finally:
        if should_close:
            await client.aclose()
