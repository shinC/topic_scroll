# [Implementation Plan] 매일경제TV (SSL 오류) 및 한국경제 (403 Forbidden) RSS 수집 에러 수정

- **작업 일시**: 2026-09-30
- **관련 요청**: 매일경제TV SSL Hostname mismatch 에러 및 한국경제 403 Forbidden 에러 해결

---

## 1. 개요 (Overview)

1. **매일경제TV (`mmoney.mk.co.kr`) SSL 에러**:
   - `https://mmoney.mk.co.kr/` 도메인은 SSL 인증서가 `mbnmoney.mbn.co.kr`로 발급되어 있어 `Hostname mismatch` 검증 오류가 발생함.
   - 실제 정상 서비스 도메인인 `https://mbnmoney.mbn.co.kr/rss/news...`로 `feeds.yaml` 설정을 갱신하고, SSL 검증 오류 발생 시 안전하게 재시도(fallback)할 수 있도록 처리.

2. **한국경제 (`hankyung.com`) 403 Forbidden 에러**:
   - Cloudflare WAF에서 브라우저형 User-Agent(Chrome 128 등)에 대해 챌린지 차단(403 Forbidden)을 적용함.
   - 반면 피드 리더용 User-Agent(`FeedFetcher-Google` 등) 또는 기본 헤더 요청 시에는 정상 200 OK를 반환함.
   - `rss_scraper.py`의 `parse_single_feed`에서 403 Forbidden 또는 네트워크/SSL 예외 발생 시 피드 리더 전용 User-Agent 및 SSL 유연 처리 fallback 로직을 적용하여 정상 수집 보장.

---

## 2. 주요 변경 사항 (Proposed Changes)

### 1) `src/config/feeds.yaml`
- 매일경제TV 7개 RSS 피드 URL을 올바른 인증서 도메인인 `https://mbnmoney.mbn.co.kr/...`로 갱신:
  - `mktv_all`: `https://mbnmoney.mbn.co.kr/rss/news`
  - `mktv_stock`: `https://mbnmoney.mbn.co.kr/rss/news/stock`
  - `mktv_estate`: `https://mbnmoney.mbn.co.kr/rss/news/estate`
  - `mktv_finance`: `https://mbnmoney.mbn.co.kr/rss/news/finance`
  - `mktv_economy`: `https://mbnmoney.mbn.co.kr/rss/news/economy`
  - `mktv_management`: `https://mbnmoney.mbn.co.kr/rss/news/management`
  - `mktv_foundation`: `https://mbnmoney.mbn.co.kr/rss/news/foundation`

### 2) `src/scrapers/implementations/rss_scraper.py`
- `parse_single_feed` 내에서 초기 요청 실패(403 Forbidden 또는 SSL/연결 예외) 시, RSS 피드 전용 User-Agent(`FeedFetcher-Google`) 및 `verify=False` 기반 Fallback 클라이언트로 자동 복구 시도 로직 구현.

---

## 3. 검증 계획 (Verification Plan)

- `python3 src/main.py run rss_news --no-sheets` 실행하여 매일경제TV 7개 및 한국경제 8개 피드가 오류 없이 100% 정상 수집되는지 검증.
- `python3 src/main.py` 전체 실행 시 경고(WARNING) 메시지 없이 전 피드 및 포털이 수집되는지 검증.
