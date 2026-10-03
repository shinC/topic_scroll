# [Walkthrough] 포모스 가십 포털 수집 추가 (100개 + 실시간/주간 인기 각 10개)

- **작업 일시**: 2026-10-02
- **관련 요청**: `https://www.fomos.kr/talk/article_list?bbs_id=4` 포털 설정 추가 (게시판 100개 + 가십 실시간 인기 10개 + 가십 주간 인기 10개 수집)

---

## 1. 작업 개요 (Overview)

포모스(FOMOS)의 가십 게시판(`https://www.fomos.kr/talk/article_list?bbs_id=4`)을 `portal.yaml`에 출처로 신규 등록하고, `PortalScraper` 내에 전용 수집 파서(`_parse_fomos`)를 구현하였습니다.
게시판의 일반 최신 게시글 100개와 함께 메인 페이지의 **가십 실시간 인기(10개)** 및 **가십 주간 인기(10개)** 항목(총 120개 항목)을 함께 수집하도록 구성하였습니다.

---

## 2. 변경 내용 (Changes Made)

1. **`src/config/portal.yaml`**:
   - `fomos_talk_gossip` 출처 신규 등록:
     - `id`: `fomos_talk_gossip`
     - `name`: "포모스 가십"
     - `publisher`: "포모스"
     - `category`: `community_gossip`
     - `url`: `https://www.fomos.kr/talk/article_list?bbs_id=4`
     - `target_count`: 100
     - `purpose`: `community`, `gossip`, `entertainment`, `talk`, `humor`

2. **`src/scrapers/implementations/portal_scraper.py`**:
   - `_parse_fomos_date`: '14:33' (당일 시:분), '09-13' (월-일), 'YYYY-MM-DD' 표기를 표준 `datetime(UTC)` 객체로 정밀 변환하는 헬퍼 메서드 추가.
   - `_parse_fomos`:
     - 1페이지 접속 시 `.postbox.left`에서 **가십 실시간 인기** 10개(`section: realtime_popular`) 추출.
     - `.postbox.right`에서 **가십 주간 인기** 10개(`section: weekly_popular`) 추출.
     - `table.board_list`에서 공지사항을 제외하고 일반 게시글의 제목, 글쓴이, 작성일시, 조회수, 추천수, 상세 URL을 파싱.
     - 목표 게시글 수(100건) 충족 시까지 페이징(`page=1, 2, 3, 4...`)을 순회 수집.
   - `parse_portal_source`: `fomos` ID 및 URL 감지 시 `_parse_fomos`로 분기 처리.

---

## 3. 검증 결과 (Verification)

- **포털 크롤러 단독 실행 테스트**:
  - `python3 src/main.py run-portal` 실행 결과:
    ```
    [포모스] 실시간 10개 + 주간 10개 + 게시판 100개 = 총 120개 수집 완료
    데이터 전처리 완료: 원본 293개 -> 중복 제거 후 235개
    [주요 포털 새소식] 235개 수집 처리 완료
    [Google Sheets] 성공적으로 235개 기사를 구글 스프레드시트에 내보냈습니다!
    ```
  - 포모스 실시간 인기 10개, 주간 인기 10개, 게시판 100개 등 총 120개 정상 파싱 확인.
  - 전처리 파이프라인 및 구글 스프레드시트 덮어쓰기 연동 검증 완료.
- **규칙 준수 확인**:
  - 자동 커밋(`git commit`) 방지 규칙 준수.
  - `REQUEST.md` 기록 및 `docs/history/` 구현 계획서/결과 보고서 작성 완료.
