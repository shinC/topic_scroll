# 구현 계획서 - Git 병합 충돌 및 GitHub 동기화 에러 수정

## 1. 개요
- **작업명**: GitHub 리모트 동기화 에러(Branch Divergence 및 Merge Conflict) 해결 및 코드 통합
- **일자**: 2026-10-06
- **목적**: 로컬 커밋과 원격(`origin/main`) 리포지토리 간의 다이버전스(divergence) 및 `.DS_Store`, `rss_scraper.py` 충돌 문제 해결하여 안정적인 수집 엔진 상태 확보.

---

## 2. 문제 원인 분석
1. **브랜치 갈라짐(Branch Divergence)**:
   - 로컬 `main` 브랜치에 커밋 `a62adf4`(`curl-cffi` 우회 로직 추가 등)가 존재하는 상태에서, 원격 `origin/main`에 신규 커밋(보건복지부 수집 추가, 포모스 추가 등) 3건이 반영되어 수동 병합/리베이스 필요.
2. **병합 충돌(Merge Conflicts)**:
   - `.DS_Store`, `src/.DS_Store`, `src/scrapers/.DS_Store`: 원격에서 삭제되었으나 로컬 커밋에서 변경 내역 기록됨.
   - `rss_scraper.py`: 403 / Cloudflare WAF 예외 처리 방식 충돌 (`httpx` 유연 폴백 vs `curl_cffi` 브라우저 임퍼소네이션).

---

## 3. 해결 방안 (Implementation Plan)
1. **.DS_Store 파일 정리**: 추적 해제 및 git index에서 완전히 삭제.
2. **rss_scraper.py 충돌 병합**:
   - `curl_cffi` 기반 Chrome 임퍼소네이션 우회 로직과 Google FeedFetcher UA + `httpx` 비검증 폴백 로직을 순차적 폴백 형태로 통합.
3. **Git Rebase 수행**:
   - `git pull --rebase origin main`을 진행하여 충돌 해결 후 완벽하게 1개의 깔끔한 선형 커밋으로 정렬.
4. **수집기 검증**:
   - `python3 src/main.py` 실행하여 포털 및 RSS 뉴스 수집과 구글 스프레드시트 내보내기가 오류 없이 정상 작동함을 검증.
