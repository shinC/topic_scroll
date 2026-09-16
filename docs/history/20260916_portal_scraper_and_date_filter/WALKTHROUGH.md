# [결과 보고서] 포털 크롤러 파싱 구조 개선 및 5일 날짜 필터링 구현 결과

- **작성일시**: 2026-09-16
- **작성자**: Antigravity AI
- **요청자**: thshin81

---

## 1. 개요 및 구현 요약

포털 사이트 크롤링 시 메인 페이지에서 무작위 링크가 수집되는 문제를 해결하고, 각 포털 사이트별 고유 게시판 및 백엔드 API 맞춤 파싱을 구현하였습니다. 또한 수집 일자 기준 5일 이상 경과한 데이터(`diff_days >= 5.0`)는 자동 필터링하여 최신 정책 및 소식만 수집 및 구글 스프레드시트에 저장하도록 개편하였습니다.

---

## 2. 주요 변경 사항

### 1) 포털별 맞춤형 파서 구축 ([portal_scraper.py](file:///app/src/scrapers/implementations/portal_scraper.py))
- **정부24 (`gov24`, `gov24_bojogum24`)**:
  - 메인 URL(`https://www.gov.kr/portal/main`) 접속 시 정책소식 페이지(`https://www.gov.kr/portal/gvrnPolicy`)로 자동 전환.
  - `goViewSubmit` 함수 ID를 기반으로 각 정책뉴스 제목, 작성일(`YYYY-MM-DD`), 상세 URL(`https://www.gov.kr/portal/gvrnPolicy/gvrnPolicyDetail?gvrnPolicyId=...`) 추출.
- **고용24 (`work24`)**:
  - 공지사항 게시판 `table tbody tr` 행 단위 파싱으로 기사 제목, 게시일자(`YYYY-MM-DD`), 상세 URL 생성.
- **복지로 (`bokjiro`)**:
  - WebSquare CSR 구조 대응을 위해 복지로 공식 JSON API (`retrieveWlfareInfoList.do`) 연동.
  - 중앙/지방 탭별 복지서비스명, 작성일(`crtDtm`), 상세 URL (`moveTWAT52005M.do?tabId=...&wlfarInfoId=...`) 수집.
- **국토교통부 (`molit`)**:
  - 보도자료 `table.tbl_lb tbody tr` 파싱으로 제목, 세부 카테고리(교통물류, 주택토지, 항공 등), 게시일자, 상세 URL 생성.

### 2) 5일 경과 데이터 자동 제외 필터링 ([processor.py](file:///app/src/pipeline/processor.py))
- `ArticleProcessor.process()` 내 5일 이상 지난 기사 제외 로직 추가:
  - 수집 기사 발행일시(`published_at`)와 현재 시각(`datetime.now(timezone.utc)`)을 비교하여 `diff_days >= 5.0`인 항목은 제외.
  - Naive & Aware Datetime 간 타임존 호환성 보장.

---

## 3. 검증 결과

### 1) 포털 전용 크롤러 수집 검증 (`python src/main.py run-portal`)
- 정부24, 고용24, 복지로, 국토교통부에서 총 **22개 항목**이 정밀 파싱되었으며, 전처리 및 중복/5일 초과 필터링 후 최신 기사만 정제되어 구글 스프레드시트에 덮어쓰기 저장 완료.

```bash
$ python src/main.py run-portal
포털 사이트 크롤링 수집 실행...
[포털 크롤러] 총 6개 사이트 수집 시작...
[포털 크롤러] 수집 완료: 총 22개 항목 수집됨 (1.08초 소요)
데이터 전처리 완료: 원본 22개 -> 중복 제거 후 11개
결과 저장 완료: data/주요_포털_새소식_20260916_052713.json
 - [주요 포털 새소식] 11개 수집 완료 -> 파일 저장: data/주요_포털_새소식_20260916_052713.json

[Google Sheets] 구글 스프레드시트로 데이터를 내보내는 중... (덮어쓰기 모드)
[Google Sheets] 성공적으로 11개 기사를 구글 스프레드시트에 내보냈습니다!
```

### 2) 5일 초과 데이터 필터링 로그 확인
- 2026-09-11 이전 발행 기사(5일 이상 지난 데이터)는 아래와 같이 자동으로 검출 및 제외됨을 확인:
  `5일 이상 경과 기사 제외 (2026-09-11, 5.2일 경과): 해외 건설 현장 안전점검 실시…`

---

## 4. 결론
요청사항에 기재된 포털 메인 링크 오수집 문제가 완전히 해결되었으며, 메인 URL 설정 대응 및 5일 날짜 필터링 규칙이 안정적으로 동작하고 있습니다.
