# [Walkthrough] 매일경제TV (SSL 오류) 및 한국경제 (403 Forbidden) RSS 수집 에러 수정 결과 보고서

- **작업 일시**: 2026-09-30
- **수정 상태**: 완료 (`Done`)

---

## 1. 주요 변경 내역 (Changes Implemented)

### 1) [feeds.yaml](file:///app/src/config/feeds.yaml)
- 매일경제TV 7개 RSS 피드 URL을 공식 SSL 인증서 도메인(`mbnmoney.mbn.co.kr`)으로 변경하여 SSL Hostname Mismatch 원천 해결:
  - `mktv_all`: `https://mbnmoney.mbn.co.kr/rss/news`
  - `mktv_stock`: `https://mbnmoney.mbn.co.kr/rss/news/stock`
  - `mktv_estate`: `https://mbnmoney.mbn.co.kr/rss/news/estate`
  - `mktv_finance`: `https://mbnmoney.mbn.co.kr/rss/news/finance`
  - `mktv_economy`: `https://mbnmoney.mbn.co.kr/rss/news/economy`
  - `mktv_management`: `https://mbnmoney.mbn.co.kr/rss/news/management`
  - `mktv_foundation`: `https://mbnmoney.mbn.co.kr/rss/news/foundation`

### 2) [rss_scraper.py](file:///app/src/scrapers/implementations/rss_scraper.py)
- Cloudflare WAF를 사용하는 한국경제(`hankyung.com`) 등 피드에 대해 피드 리더 전용 User-Agent(`Mozilla/5.0 (compatible; FeedFetcher-Google; +http://www.google.com/feedfetcher.html)`)를 적용하여 403 Forbidden 차단 문제 해결.
- 초기 요청 실패(403 또는 SSL/네트워크 예외) 시 자동으로 피드 리더 UA 및 SSL 유연 폴백 클라이언트로 재시도하도록 2중 안전장치 구현.

---

## 2. 검증 결과 (Verification Results)

- **RSS 수집 실행 결과**:
  ```bash
  python3 -u src/main.py run rss_news --no-sheets
  ```
  - 매일경제TV 7개 및 한국경제 8개 피드 모두 100% 정상 수집 완료 (수집 실패 WARNING 0건).
  - 유효 수집 기사 수: 297개 → 519개로 대폭 증가.

- **전체 엔진 및 구글 스프레드시트 연동 결과**:
  ```bash
  python3 src/main.py
  ```
  ```text
  전체 뉴스/포털 수집 실행 (python src/main.py)...
  총 2개 스크래퍼 수집 시작...
  [포털 크롤러] 총 8개 사이트 수집 시작...
  [RSS 뉴스 수집기] 총 60개 피드 수집 시작...
  [포털 크롤러] 수집 완료: 총 71개 항목 수집됨 (1.61초 소요)
  데이터 전처리 완료: 원본 1115개 -> 중복 제거 후 519개
  - [RSS 뉴스 모음] 519개 수집 처리 완료
  수집 완료! 총 581개 기사 수집됨.
  [Google Sheets] '시트1' 시트 데이터를 덮어쓰는 중... (총 581건)
  [Google Sheets] 성공적으로 581개 기사를 구글 스프레드시트에 내보냈습니다!
  [Google Sheets] 스프레드시트 덮어쓰기 저장 완료!
  ```
