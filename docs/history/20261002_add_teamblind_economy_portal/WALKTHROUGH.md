# [Walkthrough] 블라인드 경제·자산관리 포털 수집 추가 (100개 수집)

- **작업 일시**: 2026-10-02
- **관련 요청**: `https://www.teamblind.com/kr/topics/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC` 포털 설정 추가 및 100개 가져오게끔 구현

---

## 1. 작업 개요 (Overview)

직장인 커뮤니티 블라인드(TeamBlind)의 '경제·자산관리' 토픽 페이지를 `portal.yaml`에 출처로 신규 등록하고, `PortalScraper` 내에 전용 수집 파서(`_parse_teamblind`)를 구현하였습니다.
블라인드의 SSR(Server-Side Rendering) HTML 구조를 분석하여 토픽 기본 페이지 및 관련 검색 엔드포인트를 순회하며 광고를 필터링하고 중복 없이 최대 100건의 기사(제목, 본문 요약, 작성자/회사, 작성일시, URL 등)를 수집하도록 구현하였습니다.

---

## 2. 변경 내용 (Changes Made)

1. **`src/config/portal.yaml`**:
   - `teamblind_economy` 출처 신규 등록:
     - `id`: `teamblind_economy`
     - `name`: "블라인드 경제·자산관리"
     - `publisher`: "블라인드"
     - `category`: `economy_finance`
     - `url`: `https://www.teamblind.com/kr/topics/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC`
     - `target_count`: 100
     - `purpose`: `economy`, `asset_management`, `investment`, `finance`, `salary`

2. **`src/scrapers/implementations/portal_scraper.py`**:
   - `_parse_blind_date`: 블라인드 고유의 상대 작성시간 표기('28분', '4시간', '어제', '3일', '09.21', '2023.03.24.')를 표준 `datetime(UTC)` 객체로 정밀 변환하는 헬퍼 메서드 추가.
   - `_parse_teamblind`:
     - 브라우저 User-Agent 및 헤더를 구성하여 SSR HTML을 요청.
     - `.article-list-pre` 카드 셀렉터를 통해 제목, 본문 미리보기, 작성자/회사, 작성시간, 링크를 추출.
     - 외부 광고(쿠팡 파트너스 배너 등) 및 중복 게시글 필터링.
     - 기본 토픽 페이지(~47건)에 이어 경제·자산관리 관련 검색 엔드포인트를 순차적으로 탐색하여 목표 수치인 100건을 충족하도록 구현.
   - `parse_portal_source`: `teamblind` ID 및 URL 감지 시 `_parse_teamblind`로 분기 처리.

---

## 3. 검증 결과 (Verification)

- **포털 크롤러 단독 실행 테스트**:
  - `python3 src/main.py run-portal` 실행 결과:
    ```
    [블라인드] 총 100개 게시글 수집 완료
    데이터 전처리 완료: 원본 171개 -> 중복 제거 후 113개
    [주요 포털 새소식] 113개 수집 처리 완료
    [Google Sheets] 성공적으로 113개 기사를 구글 스프레드시트에 내보냈습니다!
    ```
  - 블라인드 경제·자산관리 100개 게시글 정상 수집 확인.
  - 전처리 파이프라인에서 5일 이내 최신 기사 선별 및 구글 스프레드시트 덮어쓰기 내보내기 정상 동작 확인.
- **규칙 준수 확인**:
  - 자동 커밋(`git commit`) 방지 규칙 준수.
  - `REQUEST.md` 기록 및 `docs/history/` 구현 계획서/결과 보고서 작성 완료.
