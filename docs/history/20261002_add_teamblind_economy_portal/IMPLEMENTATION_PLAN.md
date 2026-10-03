# [Implementation Plan] 블라인드 경제·자산관리 포털 수집 추가 (100개 수집)

- **작업 일시**: 2026-10-02
- **관련 요청**: `https://www.teamblind.com/kr/topics/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC` 포털 설정 추가 및 100개 게시글 수집

---

## 1. 개요 (Overview)

블라인드(TeamBlind)의 직장인 경제·자산관리 토픽(`https://www.teamblind.com/kr/topics/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC`)을 `portal.yaml`에 신규 출처로 등록하고, 포털 크롤러(`PortalScraper`)에 전용 파서를 구현하여 최대 100개의 최신 게시글(제목, 내용 요약, 작성자/회사, 작성일시, URL 등)을 안전하게 수집할 수 있도록 지원합니다.

---

## 2. 변경 설계 (Proposed Changes)

### 1) `src/config/portal.yaml`
- 신규 포털 소스 추가:
  - `id`: `teamblind_economy`
  - `name`: "블라인드 경제·자산관리"
  - `publisher`: "블라인드"
  - `category`: `economy_finance`
  - `type`: `portal`
  - `url`: `https://www.teamblind.com/kr/topics/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC`
  - `enabled`: `true`
  - `crawler`: `page`
  - `priority`: `1`
  - `target_count`: `100`
  - `purpose`: `economy`, `asset_management`, `investment`, `finance`, `salary`

### 2) `src/scrapers/implementations/portal_scraper.py`
- `_parse_teamblind(source_cfg, client)` 전용 파서 구현:
  - 블라인드 SSR HTML 구조 분석을 통해 `.article-list-pre` 카드 추출
  - 광고 배너(쿠팡 등 외부 제휴 광고) 필터링
  - 단일 페이지(SSR 기본 47개)를 초과하여 요청된 100개 목표 수집을 달성하기 위해 토픽 기본 URL 및 경제·자산관리 관련 검색 엔드포인트를 순회하며 중복 없이 최대 100건 수집
  - 상대 시간(예: '28분', '4시간', '어제', 'MM.DD', 'YYYY.MM.DD')을 표준 `datetime(UTC)`으로 정밀 변환
  - `parse_portal_source` 라우터에 `teamblind` 분기 연동

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run-portal` 실행을 통해 블라인드 경제·자산관리 항목에서 정확히 100건의 기사가 수집되는지 검증
- 수집된 기사의 ID, 제목, 본문, 작성일시, URL 및 메타데이터 필드 무결성 확인
- 기존 포털 사이트 수집에 영향이 없는지 전체 실행 확인
