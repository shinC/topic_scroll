# [Walkthrough] 블라인드 토픽 베스트(teamblind.com) 포털 수집 추가

- **작업 일시**: 2026-10-03
- **관련 요청**: `https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8` <-- 포털에 추가

---

## 1. 작업 개요 (Overview)

직장인 커뮤니티 블라인드(TeamBlind)의 '토픽 베스트' 페이지(`https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8`)를 `portal.yaml`에 신규 출처로 등록하고, `PortalScraper` 내 블라인드 전용 파서(`_parse_teamblind`)를 각 토픽 출처에 맞게 유연하게 동작하도록 개선하였습니다.

---

## 2. 변경 내용 (Changes Made)

1. **`src/config/portal.yaml`**:
   - `teamblind_topic_best` 출처 신규 등록:
     - `id`: `teamblind_topic_best`
     - `name`: "블라인드 토픽 베스트"
     - `publisher`: "블라인드"
     - `category`: `community_best`
     - `type`: `portal`
     - `url`: `https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8`
     - `target_count`: 100
     - `purpose`: `community`, `topic`, `best`, `trending`, `popular`

2. **`src/scrapers/implementations/portal_scraper.py`**:
   - `_parse_teamblind` 파서 개선:
     - 기존 `teamblind_economy` 전용으로 하드코딩되어 있던 보조 검색 URL(`search/경제·자산관리` 등)을 `portal_id == "teamblind_economy"` 조건에서만 확장하도록 분기하여, 토픽 베스트 수집 시 경제 검색 결과가 혼입되지 않고 토픽 베스트 페이지 본연의 베스트 게시글을 수집하도록 수정.
     - 토픽 베스트 카드에 명시된 개별 토픽 분류(`.category a.topic-name`, 예: '썸·연애', '결혼생활', '부동산', '주식·투자' 등)를 파싱하여 `category` 및 `extra_meta["topic"]`에 정확히 반영.
     - 작성자 텍스트의 불필요한 줄바꿈 및 다중 공백을 정제(`" ".join(...)`).
     - 수집 완료 로그에 `portal_id`를 명시(`[블라인드 - {portal_id}] 총 {len(articles)}개 게시글 수집 완료`)하여 다중 블라인드 토픽 수집 시 출처별 진행 상태 확인 용이.

---

## 3. 검증 결과 (Verification)

1. **YAML 구문 및 포털 출처 검증**:
   - `portal.yaml` 구문 분석 결과 총 11개 포털 출처 정상 로드 확인 (`teamblind_economy`, `teamblind_topic_best` 포함).
2. **스크래퍼 등록 확인**:
   - `PYTHONPATH=src python3 src/main.py list` 정상 등록 및 실행 확인 (`portal_news`, `rss_news`).
3. **블라인드 토픽 베스트 HTML 파싱 검증**:
   - SSR HTML 내 `article-list-pre` 카드 추출, 제목/내용 요약/작성자/상대 작성시간 변환/개별 카테고리 추출 정상 동작 확인 (광고 배너 및 중복 필터링 적용).
4. **규칙 준수**:
   - Git 자동 커밋 방지 지침 준수.
   - `REQUEST.md` 기록 및 `docs/history/` 문서 생성 완료.
