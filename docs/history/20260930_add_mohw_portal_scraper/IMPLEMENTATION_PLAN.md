# [Implementation Plan] 보건복지부 (mohw.go.kr) 보도자료 수집기 추가

- **작업 일시**: 2026-09-30
- **관련 요청**: 보건복지부 보도자료(`https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027`)를 `portal.yaml`에 추가 및 크롤링 연동

---

## 1. 개요 (Overview)

보건복지부의 공식 보도자료 목록 페이지(`https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027`)를 `portal.yaml` 포털 수집 대상으로 신규 등록하고, `portal_scraper.py` 내 전용 파서(`_parse_mohw`)를 구현하여 복지/보건 관련 최신 보도자료를 자동 수집하고 파이프라인(구글 스프레드시트/로컬 데이터)과 연동합니다.

---

## 2. 주요 변경 사항 (Proposed Changes)

### 1) `src/config/portal.yaml`
- `mohw_press_release` (보건복지부 보도자료) 포털 출처 신규 등록:
  - id: `mohw_press_release`
  - name: `"보건복지부 보도자료"`
  - publisher: `"보건복지부"`
  - category: `welfare_policy`
  - url: `"https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027"`
  - purpose: `[welfare, healthcare, press_release, policy]`

### 2) `src/scrapers/implementations/portal_scraper.py`
- `_parse_mohw` 전용 파서 구현:
  - `table.tstyle_list tbody tr` 테이블 구조 파싱
  - 제목에서 뱃지 태그(`<span class="sr_only">새글</span>`, 아이콘 등) 제거 및 순수 텍스트 정제
  - 담당부서(department), 등록일자, 게시물 고유 번호(`list_no`), 상세 URL 추출
- `parse_portal_source` 분기 라우터에 `mohw.go.kr` 라우팅 추가 (기존 `gov.kr` 판별보다 앞서 배치하여 오분기 방지).

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run-portal --no-sheets` 실행하여 보건복지부 포함 총 9개 포털 소식 정상 수집 여부 및 보건복지부 보도자료 기사 파싱(제목, 날짜, URL 등) 정상 동작 검증.
