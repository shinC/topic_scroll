# [Implementation Plan] 포모스 가십 포털 수집 추가 (100개 + 실시간/주간 인기 각 10개)

- **작업 일시**: 2026-10-02
- **관련 요청**: `https://www.fomos.kr/talk/article_list?bbs_id=4` 포털 설정 추가 (게시판 100개 + 가십 실시간 인기 10개 + 가십 주간 인기 10개 수집)

---

## 1. 개요 (Overview)

게임 및 엔터테인먼트 커뮤니티 포모스(FOMOS)의 가십 게시판(`https://www.fomos.kr/talk/article_list?bbs_id=4`)을 `portal.yaml`에 신규 출처로 등록하고, `PortalScraper` 내에 전용 수집 파서(`_parse_fomos`)를 구현합니다.
게시판의 일반 최신 게시글 100개뿐만 아니라 우측/좌측 박스에 제공되는 **가십 실시간 인기(10개)** 및 **가십 주간 인기(10개)** 항목을 함께 수집하도록 구성합니다.

---

## 2. 변경 설계 (Proposed Changes)

### 1) `src/config/portal.yaml`
- 신규 포털 소스 추가:
  - `id`: `fomos_talk_gossip`
  - `name`: "포모스 가십"
  - `publisher`: "포모스"
  - `category`: `community_gossip`
  - `type`: `portal`
  - `url`: `https://www.fomos.kr/talk/article_list?bbs_id=4`
  - `enabled`: `true`
  - `crawler`: `page`
  - `priority`: `1`
  - `target_count`: `100`
  - `purpose`: `community`, `gossip`, `entertainment`, `talk`, `humor`

### 2) `src/scrapers/implementations/portal_scraper.py`
- `_parse_fomos_date(date_str)` 헬퍼 구현:
  - '14:33' (당일 시간) -> 당일 UTC datetime 변환
  - '09-13' (월-일) -> 당해 연도 UTC datetime 변환
  - 'YYYY-MM-DD' -> 정규 변환
- `_parse_fomos(source_cfg, client)` 전용 파서 구현:
  - 1페이지 접속 시:
    - `.postbox.left`에서 **가십 실시간 인기** 10개 추출 (`section: realtime_popular`)
    - `.postbox.right`에서 **가십 주간 인기** 10개 추출 (`section: weekly_popular`)
  - 게시판 페이징(`page=1, 2, 3, 4...`):
    - `table.board_list`에서 공지사항을 제외하고 일반 게시글 파싱
    - 제목, 작성자, 작성일시, 조회수, 추천수, 상세 URL 추출
    - 목표 건수(기본 100건) 충족 시까지 순회
  - `parse_portal_source` 라우터에 `fomos` 분기 연동

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run-portal` 실행:
  - 가십 실시간 인기 10개, 주간 인기 10개, 게시판 100개 등 총 120개의 포모스 기사가 정상 파싱되는지 검증
  - 전처리 파이프라인 및 구글 스프레드시트 내보내기 정상 동작 검증
- 기존 포털 사이트 수집 영향도 및 예외 처리 검증
