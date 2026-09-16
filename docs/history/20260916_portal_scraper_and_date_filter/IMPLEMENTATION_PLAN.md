# [계획서] 포털 크롤러 파싱 구조 개선 및 5일 날짜 필터링 적용

- **작성일시**: 2026-09-16
- **작성자**: Antigravity AI
- **요청자**: thshin81

---

## 1. 개요 및 목적
기존 포털 크롤링 시 메인 페이지의 임의 `a[href]` 링크를 수집하던 문제점을 수정하고, 각 기관 포털(정부24, 고용24, 복지로, 국토교통부)의 서비스/정책 목록 구조 및 전용 백엔드 API를 정확히 파싱하도록 개선합니다. 또한, 수집된 기사/정책 항목의 발행일시가 크롤링 수행 시점 대비 5일 이상 지난 경우(`diff_days >= 5.0`) 결과에서 자동으로 제외하는 날짜 필터링 시스템을 구축합니다.

---

## 2. 세부 구현 내용

1. **포털 사이트별 맞춤형 파서 구현 (`src/scrapers/implementations/portal_scraper.py`)**
   - **정부24 / 보조금24 (`gov24`, `gov24_bojogum24`)**: 메인 URL 접속 시 정책/서비스 소식 URL(`gvrnPolicy`)로 자동 연결. `goViewSubmit` 자바스크립트 함수 대상 기사 파싱, 작성일시 `<span class="date">` 또는 `YYYY-MM-DD` 파싱, 상세페이지 URL 매핑.
   - **고용24 (`work24`)**: 공지/뉴스 게시판 `table tbody tr` 행 단위 파싱, 게시일시 `YYYY-MM-DD` 파싱, 상세페이지 URL 연결.
   - **복지로 (`bokjiro`)**: WebSquare 클라이언트 렌더링 방식 대응을 위해 복지로 공식 JSON API (`retrieveWlfareInfoList.do`) 연동. `tabId=1`(중앙), `tabId=2`(지방) 복지서비스명, 작성일(`crtDtm`), 상세 URL 연결.
   - **국토교통부 (`molit`)**: 보도자료 게시판 `table.tbl_lb tbody tr` 파싱, 카테고리, 게시일자, 상세 URL 연결.

2. **5일 날짜 필터링 구현 (`src/pipeline/processor.py`)**
   - `ArticleProcessor.process()` 단계에서 기사별 `published_at`과 현재 시간(`datetime.now(timezone.utc)`) 간의 차이(`diff_days`) 계산.
   - `diff_days >= 5.0` (5일 이상 차이나는 데이터) 항목은 로깅 및 제외 처리.
   - naive `datetime`과 aware `datetime` 호환 처리.

---

## 3. 검증 계획
- CLI 명령어 실행 (`python src/main.py run-portal`, `python src/main.py run-rss`, `python src/main.py run-all`)
- 수집된 기사의 작성일시(`published_at`) 및 5일 필터링 동작 결과 확인.
