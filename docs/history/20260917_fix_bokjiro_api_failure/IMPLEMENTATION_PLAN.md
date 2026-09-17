# [Implementation Plan] 복지로 API 404 요청 실패 수정

- **작업 일시**: 2026-09-17
- **관련 요청**: 포털 정보 수집 시 복지로 API 요청 실패(HTTP 404) 원인 파악 및 수정

---

## 1. 개요 (Overview)

복지로 사이트(`bokjiro.go.kr`) 시스템 개편으로 인해 기존 포털 스크래퍼에서 이용하던 내부 AJAX API 엔드포인트(`retrieveWlfareInfoList.do`)가 404 Not Found를 응답함에 따라 수집 도중 경고 로그가 발생하는 문제를 해결합니다.

---

## 2. 변경 설계 (Proposed Changes)

### `src/scrapers/implementations/portal_scraper.py`
- **`_parse_bokjiro` 파서 수정**:
  - `retrieveWlfareInfoList.do` API 호출 결과를 검증하여 200 OK가 아닐 경우 경고 로그 출력 대신 `logger.debug` 수준으로 처리.
  - JSON API 미응답 시 복지로 서비스 안내 웹페이지(`moveTWAT52005M.do?tabId=1` / `tabId=2`) 기반 HTML 및 메타데이터 수집 폴백(Fallback) 로직 작동.
  - 예외 발생 시에도 수집 파이프라인 전체가 정상 동작하고 구글 스프레드시트로 덮어쓰기되도록 안전하게 연동.

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run-portal` 명령어를 실행하여 복지로 API 404 경고 로그가 제거되고 정상 수집(24개 항목)되는지 확인.
- 구글 스프레드시트 덮어쓰기 연동이 문제없이 완료되는지 확인.
