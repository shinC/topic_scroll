# [계획서] 블로그 주제 선정을 위한 데이터 수집 및 구글 스프레드시트 연동

- **작성일시**: 2026-09-09
- **작성자**: Antigravity AI
- **요청자**: thshin81

---

## 1. 개요 및 목적
블로그 주제 선정을 위해 `src/config/` 내의 `feeds.yaml`, `keywords.yaml`, `portal.yaml` 설정을 기반으로 최신 뉴스(제목, 날짜, 링크, 출처 등)를 RSS 및 웹 크롤링으로 자동 수집하고, 구글 스프레드시트(Google Sheets)에 자동 저장하는 수집 엔진 구현 계획입니다.

---

## 2. 구글 스프레드시트 연동 필요 정보
1. **GCP 서비스 계정 키 파일 (JSON 파일)**
2. **구글 스프레드시트 ID (Spreadsheet ID)**
3. **스프레드시트 공유 권한 설정 (서비스 계정 이메일 편집자 권한)**

---

## 3. 사용자 확인 및 변경 결정 사항
1. **스프레드시트 저장 방식**: 매번 수집 시 기존 행 덮어쓰기(`clear()` 후 작성) 방식 확정.
2. **수집 범위 제한**: RSS 피드 수집 시 한 번에 가져올 기사 수를 피드당 최대 **20개**로 제한 확정.
3. **독립 실행 구조**: 포털 크롤러(`run-portal`)와 RSS 피드 수집기(`run-rss`)를 개별적으로 실행 가능하도록 독립화 확정.

---

## 4. 세부 구현 내용
- `src/config.py`: YAML 로더 유틸리티 및 구글 스프레드시트 설정 항목 추가
- `src/scrapers/implementations/rss_scraper.py`: RSS 60개 피드 수집기 구현
- `src/scrapers/implementations/portal_scraper.py`: 포털 사이트 공지/소식 크롤러 구현
- `src/pipeline/processor.py`: `keywords.yaml` 기반 카테고리/태그 자동 분류
- `src/pipeline/google_sheets_exporter.py`: `gspread` 연동 덮어쓰기 모드 엑스포터 구현
- `src/main.py`: `run-rss`, `run-portal`, `run-all` CLI 명령어 개편 및 기본 실행 대응

---

## 5. 검증 계획
- YAML 설정 로딩 테스트 및 개별 수집기 단위 동작 테스트
- 구글 스프레드시트 연동 및 덮어쓰기 데이터 쓰기 검증
