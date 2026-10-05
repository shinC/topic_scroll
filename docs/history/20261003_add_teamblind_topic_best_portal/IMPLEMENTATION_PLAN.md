# [Implementation Plan] 블라인드 토픽 베스트(teamblind.com) 포털 수집 추가

- **작업 일시**: 2026-10-03
- **관련 요청**: `https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8` <-- 포털에 추가

---

## 1. 작업 개요 (Overview)

직장인 커뮤니티 블라인드(TeamBlind)의 '토픽 베스트'(`https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8`) 페이지를 `portal.yaml`에 신규 출처로 등록하고, 기존 `PortalScraper` 내 블라인드 수집 파서(`_parse_teamblind`)가 각 토픽 출처에 맞게 유연하게 동작하도록 개선합니다.

---

## 2. 변경 설계 (Design & Proposed Changes)

### 2.1 `src/config/portal.yaml`
- `teamblind_topic_best` 출처 신규 추가:
  ```yaml
  - id: teamblind_topic_best
    name: "블라인드 토픽 베스트"
    publisher: "블라인드"
    category: community_best
    type: portal
    url: "https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8"
    enabled: true
    crawler: page
    priority: 1
    target_count: 100
    purpose:
      - community
      - topic
      - best
      - trending
      - popular
  ```

### 2.2 `src/scrapers/implementations/portal_scraper.py`
- `_parse_teamblind`:
  - 기존에 `teamblind_economy` 검색 URL(`search/경제·자산관리` 등)이 모든 블라인드 출처에 고정 적용되던 로직을 분기 처리:
    - `portal_id == "teamblind_economy"`일 때만 경제·자산관리 검색 엔드포인트 확장 적용.
    - 일반 토픽(토픽 베스트 등)은 해당 토픽 고유의 URL에서 게시글 수집.
  - 토픽 베스트 카드의 개별 토픽 태그(`.category a.topic-name`)를 추출하여 기사 카테고리(`category`) 및 `extra_meta["topic"]`에 반영.
  - 작성자 텍스트 줄바꿈 및 불필요 공백 정제(`" ".join(author_el.get_text().split())`).
  - 로깅 메시지에 `portal_id`를 표기하여 다중 블라인드 토픽 수집 시 식별 용이성 제공.

---

## 3. 검증 계획 (Verification Plan)

- `portal.yaml` YAML 유효성 검증.
- `portal_scraper.py` 파서 로직 및 데이터 매핑 검증.
- Git 자동 커밋 방지 및 `REQUEST.md` 기록 준수.
