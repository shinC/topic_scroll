# [Implementation Plan] 대한민국 정책브리핑 (korea.kr) 정책뉴스 및 보도자료 수집기 추가

- **작업 일시**: 2026-09-17
- **관련 요청**: 대한민국 정책브리핑 사이트(정책뉴스, 보도자료) 포탈 수집 대상 추가 및 크롤링 연동

---

## 1. 개요 (Overview)

대한민국 정책브리핑의 정책뉴스(`https://www.korea.kr/news/policyNewsList.do`)와 보도자료(`https://www.korea.kr/briefing/pressReleaseList.do`)를 `portal.yaml` 포털 수집 대상으로 신규 등록하고, `portal_scraper.py` 내 전용 파서(`_parse_korea_kr`)를 구현하여 수집 및 구글 스프레드시트 연동을 수행합니다.

---

## 2. 주요 변경 사항 (Proposed Changes)

### 1) `src/config/portal.yaml`
- `korea_policy_news` (정책뉴스) 및 `korea_press_release` (보도자료) 포털 출처 2건 등록.

### 2) `src/scrapers/implementations/portal_scraper.py`
- `_parse_korea_kr` 전용 파서 구현 (제목, 작성일, 출처, 상세 URL 추출).
- `parse_portal_source` 분기 라우터에 `korea.kr` 연동 추가.

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run-portal` 실행하여 대한민국 정책브리핑 포함 총 8개 포털 소식 정상 수집 검증.
