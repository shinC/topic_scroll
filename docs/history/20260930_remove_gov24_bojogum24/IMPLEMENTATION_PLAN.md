# [Implementation Plan] 정부24 보조금24 (gov24_bojogum24) 설정 및 소스코드 정리

- **작업 일시**: 2026-09-30
- **관련 요청**: `portal.yaml`에서 `gov24_bojogum24` 항목 제거 및 관련 소스코드 내 참조 정리

---

## 1. 개요 (Overview)

`gov24_bojogum24`는 정부24 내 중복되는 서비스로 별도 크롤링 항목에서 제외하고, `portal.yaml` 및 `portal_scraper.py` 내의 관련 주석/파서 로직을 깔끔하게 정리합니다.

---

## 2. 주요 변경 사항 (Proposed Changes)

### 1) `src/config/portal.yaml`
- `gov24_bojogum24` 항목 및 설명 주석 삭제.
- 섹션 타이틀을 `# 정부24 / 보조금24`에서 `# 정부24`로 수정.

### 2) `src/scrapers/implementations/portal_scraper.py`
- `_parse_gov24` docstring에서 "보조금24" 관련 문구 정리.

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run-portal --no-sheets` 실행하여 `gov24_bojogum24` 없이 정부24 및 보건복지부를 포함한 8개 포털이 정상적으로 수집되는지 검증.
