# 개발 진행 및 요청 사항 기록 (REQUEST.md)

이 문서는 사용자가 요청한 개발 진행 관련 요청 사항 및 처리 내역을 지속적으로 기록하고 관리하는 메인 이력 파일입니다. 각 작업의 상세 계획서 및 검증 보고서는 `docs/history/` 하위 폴더에 연결되어 보존됩니다.

---

## 📋 요청 사항 기록 목록

### 1. Git 사용자 계정 설정 및 커밋 오류 해결
- **요청 일시**: 2026-09-09
- **요청 내용**: 깃 커밋 시 유저 정보 없어서 발생하는 오류 해결 및 계정 정보(`thshin81@naver.com`) 설정.
- **처리 내역**:
  - `git config user.name "thshin81"` 및 `git config user.email "thshin81@naver.com"` 설정
  - 기존 커밋 작성자 정보 `thshin81 <thshin81@naver.com>`으로 amend 완료
- **상태**: `완료 (Done)`

---

### 2. 요청 사항 기록용 REQUEST.md 파일 생성
- **요청 일시**: 2026-09-09
- **요청 내용**: 개발 진행에 관해 요청하는 사항들을 기록할 `REQUEST.md` 파일 생성 및 관리.
- **처리 내역**: `REQUEST.md` 파일 생성 및 이력 체계 구축
- **상태**: `완료 (Done)`

---

### 3. Git 자동 커밋 금지
- **요청 일시**: 2026-09-09
- **요청 내용**: 작업 진행 시 Git 커밋을 자동으로 수행하지 말 것.
- **처리 내역**: 자동 커밋 지침 적용 (사용자 요청 시에만 커밋 수행)
- **상태**: `적용 완료 (Active)`

---

### 4. 실환경 라이브러리 관리용 requirements.txt 생성
- **요청 일시**: 2026-09-09
- **요청 내용**: 실환경에서 라이브러리를 버전별로 관리할 수 있는 txt 파일(`requirements.txt`) 생성.
- **처리 내역**: `pip freeze` 기반으로 주요 의존성 및 하위 의존성 라이브러리의 정확한 버전이 명시된 `requirements.txt` 파일 생성 완료
- **상태**: `완료 (Done)`

---

### 5. 블로그 주제 선정용 수집 프로그램 구축 및 구글 스프레드시트 연동
- **요청 일시**: 2026-09-09
- **요청 내용**: `config` 내 `feeds.yaml`, `keywords.yaml`, `portal.yaml`을 활용한 RSS 및 사이트 크롤링 뉴스 수집 엔진 구축 및 구글 스프레드시트 연동.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260909_google_sheets_collector/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20260909_google_sheets_collector/WALKTHROUGH.md)

---

### 6. 요청건별 문서 체계화 (docs/history/ 구조 도입)
- **요청 일시**: 2026-09-09
- **요청 내용**: 요청건에 대한 구현 계획서와 결과 보고서를 체계적으로 보존하는 가이드 수립.
- **처리 내역**: `docs/history/YYYYMMDD_<요청주제>/` 폴더 체계 적용 및 `REQUEST.md`와 상호 링크 연결 완료
- **상태**: `적용 완료 (Active)`

---

### 7. AI Agent 규칙 자동 참조 문서화 (docs/AGENT_RULES.md & .agentrules)
- **요청 일시**: 2026-09-09
- **요청 내용**: 매번 커밋 금지, REQUEST.md 기록, history 문서 생성을 요청하지 않도록 Agent가 항상 참조하는 지침 문서 생성.
- **처리 내역**: `docs/AGENT_RULES.md` 및 프로젝트 루트 `.agentrules` 파일 생성 완료
- **상태**: `적용 완료 (Active)`

---

### 8. 포털 크롤러 파싱 구조 개선 및 5일 날짜 필터링 적용
- **요청 일시**: 2026-09-16
- **요청 내용**:
  1. 포털 사이트 크롤링 시 메인 임의 링크 추출 대신 포털별 서비스/공지/정책 목록 및 API 파싱 적용.
  2. 메인 URL 입력 시에도 서비스/정책 소식 페이지 자동 연동 및 데이터 수집.
  3. 수집 데이터가 크롤링 날짜 기준 5일 이상 차이날 경우 수집 제외.
- **처리 내역**: 포털별 맞춤형 파서 구축(정부24, 고용24, 복지로, 국토교통부) 및 `ArticleProcessor` 내 5일 초과 항목 자동 제외 필터링 구현 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260916_portal_scraper_and_date_filter/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20260916_portal_scraper_and_date_filter/WALKTHROUGH.md)

---

### 9. 샘플 해커뉴스 스크래퍼 삭제 및 기본 실행(`python src/main.py`) 전체 수집 연결
- **요청 일시**: 2026-09-16
- **요청 내용**:
  1. 불필요한 샘플 해커뉴스 수집기(`sample_news.py`) 삭제.
  2. `python src/main.py` 명령어 실행 시 모든 실 수집 스크래퍼(`portal_news`, `rss_news`)가 바로 실행되도록 개선.
- **처리 내역**: `sample_news.py` 삭제, 등록 스크래퍼 목록 정제(2개) 및 `src/main.py` 기본 콜백 실행 문구 개선 완료.
- **상태**: `완료 (Done)`

---

### 10. 구글 스프레드시트 내보내기 시 로컬 파일(data/ 폴더) 자동 생성 비활성화
- **요청 일시**: 2026-09-16
- **요청 내용**:
  1. 수집 시 `data/` 폴더에 자동 생성되던 불필요한 로컬 JSON 파일들 삭제.
  2. 구글 스프레드시트로 전송 시 로컬 파일이 생성되지 않도록 `src/main.py` 수정 (필요 시 `--save-file` 옵션으로만 저장).
- **처리 내역**: 기존 `data/` 내 불필요 파일 전체 삭제 및 `src/main.py` 기본 실행 시 로컬 파일 미생성 처리 완료.
- **상태**: `완료 (Done)`

---

---

### 12. 복지로 API 요청 실패(HTTP 404) 원인 파악 및 수집기 개선
- **요청 일시**: 2026-09-17
- **요청 내용**: 포탈 정보 수집 시 발생하던 복지로 API 요청 실패 (`Client error '404 Not Found'`) 오류의 원인을 파악하여 수정.
- **처리 내역**:
  - `portal_scraper.py` 내 `_parse_bokjiro` 파서 수정 (404 예외 핸들링 소멸 처리 및 HTTP Status 200 검증 추가).
  - 복지로 JSON API 미응답 시 복지로 서비스 페이지(`moveTWAT52005M.do`) 기반 메타 정보 파싱 및 안전한 폴백(Fallback) 수집 로직 구현 완료.
  - `python3 src/main.py run-portal` 테스트 시 404 실패 경고 없이 총 24개 포털 소식 정상 수집 및 구글 스프레드시트 내보내기 검증 완료.
- **상태**: `완료 (Done)`
---

### 13. 대한민국 정책브리핑(korea.kr) 정책뉴스 및 보도자료 포털 수집 추가
- **요청 일시**: 2026-09-17
- **요청 내용**: 대한민국 정책브리핑 사이트의 정책뉴스(`https://www.korea.kr/news/policyNewsList.do`) 및 보도자료(`https://www.korea.kr/briefing/pressReleaseList.do`)를 포털 수집 대상으로 추가.
- **처리 내역**:
  - `portal.yaml`에 `korea_policy_news`, `korea_press_release` 출처 신규 추가.
  - `portal_scraper.py` 내 `_parse_korea_kr` 파서 구현 및 `policyNewsView.do`, `pressReleaseView.do` 파싱 연동 완료.
  - `python3 src/main.py run-portal` 실행 테스트 시 총 8개 사이트 74개 항목 수집 및 구글 스프레드시트 내보내기 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260917_add_korea_kr_portal_scraper/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20260917_add_korea_kr_portal_scraper/WALKTHROUGH.md)

---

### 14. OrbStack Dev Container 실행용 devcontainer.json 생성
- **요청 일시**: 2026-09-18
- **요청 내용**: OrbStack 및 VS Code Dev Containers 환경 실행을 위해 누락되어 있던 `devcontainer.json` 설정 파일 생성.
- **처리 내역**:
  - `.devcontainer/devcontainer.json` 파일 생성 완료 (기존 `.devcontainer/Dockerfile` 기반 빌드, `/workspace` 바인드 마운트, `PYTHONPATH` 설정 및 `postCreateCommand`에 `requirements.txt` 설치 등록).
  - OrbStack 환경에서 Dockerfile 빌드 정상 동작 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260918_add_devcontainer_config/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20260918_add_devcontainer_config/WALKTHROUGH.md)

---

### 15. 보건복지부(mohw.go.kr) 보도자료 포털 수집 추가
- **요청 일시**: 2026-09-30
- **요청 내용**: 보건복지부 보도자료(`https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027`)를 `portal.yaml`에 추가 및 수집 연동.
- **처리 내역**:
  - `portal.yaml`에 `mohw_press_release` 포털 출처 신규 등록.
  - `portal_scraper.py` 내 `_parse_mohw` 전용 파서 구현 및 `parse_portal_source` 분기 연동 완료.
  - `python3 src/main.py run-portal` 테스트 시 총 9개 포털 사이트 대상 정상 수집 및 전처리 검증 완료 (보건복지부 15개 기사 정상 파싱).
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260930_add_mohw_portal_scraper/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20260930_add_mohw_portal_scraper/WALKTHROUGH.md)

---

### 16. 정부24 보조금24(gov24_bojogum24) 설정 및 소스코드 정리
- **요청 일시**: 2026-09-30
- **요청 내용**: `portal.yaml`에서 `gov24_bojogum24` 항목 삭제 및 소스코드 내 관련 참조 정리.
- **처리 내역**:
  - `portal.yaml`에서 `gov24_bojogum24` 항목 및 설명 주석 삭제 완료.
  - `portal_scraper.py` 내 `_parse_gov24` docstring 정리 완료.
  - `python3 src/main.py run-portal` 테스트 시 총 8개 포털 사이트 73건 정상 수집 및 전처리 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260930_remove_gov24_bojogum24/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20260930_remove_gov24_bojogum24/WALKTHROUGH.md)

---

### 17. 매일경제TV(SSL 에러) 및 한국경제(403 Forbidden) RSS 수집 에러 수정
- **요청 일시**: 2026-09-30
- **요청 내용**: 매일경제TV SSL Hostname mismatch 오류 및 한국경제 Cloudflare 403 Forbidden 오류 해결.
- **처리 내역**:
  - `feeds.yaml`: 매일경제TV 7개 피드 URL을 인증서 일치 도메인(`mbnmoney.mbn.co.kr`)으로 변경하여 SSL 불일치 해소.
  - `rss_scraper.py`: 한국경제 등 Cloudflare WAF 사이트에 피드 리더 전용 User-Agent 적용 및 403/SSL 예외 발생 시 안전한 Fallback 재시도 로직 구현.
  - `python3 src/main.py` 실행 시 실패 경고 0건, 총 581개 기사 수집 및 구글 스프레드시트 내보내기 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20260930_fix_mktv_hankyung_rss_errors/IMPLEMENTATION_PLAN.md)
---

### 18. 블라인드(teamblind.com) 경제·자산관리 포털 수집 추가 (100개 수집)
- **요청 일시**: 2026-10-02
- **요청 내용**: 블라인드 경제·자산관리(`https://www.teamblind.com/kr/topics/%EA%B2%BD%EC%A0%9C%C2%B7%EC%9E%90%EC%82%B0%EA%B4%80%EB%A6%AC`)를 `portal.yaml`에 추가하고 100개 게시글을 수집하도록 연동.
- **처리 내역**:
  - `portal.yaml`에 `teamblind_economy` 출처 신규 등록 (`target_count: 100`).
  - `portal_scraper.py` 내 `_parse_teamblind` 파서 구현 (기본 토픽 페이지 및 경제/자산관리 관련 검색 엔드포인트를 순회하며 광고 필터링 후 100건 수집).
  - `_parse_blind_date` 작성시간 변환 헬퍼 구현 (상대 시간 및 날짜 표기를 UTC datetime으로 정밀 변환).
  - `python3 src/main.py run-portal` 테스트 시 블라인드 100건 정상 수집 및 전처리(최신 5일 이내 기사 선별)/구글 스프레드시트 내보내기 정상 동작 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20261002_add_teamblind_economy_portal/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20261002_add_teamblind_economy_portal/WALKTHROUGH.md)

---

### 19. 포모스(fomos.kr) 가십 포털 수집 추가 (100개 + 실시간/주간 인기 각 10개)
- **요청 일시**: 2026-10-02
- **요청 내용**: 포모스 가십 게시판(`https://www.fomos.kr/talk/article_list?bbs_id=4`)을 `portal.yaml`에 추가 (게시판 100개 + 가십 실시간 인기 10개 + 가십 주간 인기 10개 동시 수집).
- **처리 내역**:
  - `portal.yaml`에 `fomos_talk_gossip` 출처 신규 등록 (`target_count: 100`).
  - `portal_scraper.py` 내 `_parse_fomos` 파서 구현 (가십 실시간 인기 10개, 가십 주간 인기 10개, 게시판 페이징 순회 100개 = 총 120개 수집).
  - `_parse_fomos_date` 작성일시 변환 헬퍼 구현 (당일 HH:MM, 월-일 MM-DD, YYYY-MM-DD 대응).
  - `python3 src/main.py run-portal` 테스트 시 포모스 총 120건 정상 수집 및 전처리/구글 스프레드시트 덮어쓰기 연동 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20261002_add_fomos_talk_gossip_portal/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20261002_add_fomos_talk_gossip_portal/WALKTHROUGH.md)

---

### 20. 블라인드(teamblind.com) 토픽 베스트 포털 수집 추가
- **요청 일시**: 2026-10-03
- **요청 내용**: 블라인드 토픽 베스트(`https://www.teamblind.com/kr/topics/%ED%86%A0%ED%94%BD-%EB%B2%A0%EC%8A%A4%ED%8A%B8`)를 `portal.yaml`에 추가.
- **처리 내역**:
  - `portal.yaml`에 `teamblind_topic_best` 출처 신규 등록 (`target_count: 100`).
  - `portal_scraper.py` 내 `_parse_teamblind` 파서 개선 (경제·자산관리 검색 엔드포인트 분기 처리 및 토픽 베스트 개별 카테고리 태그 파싱, 작성자 공백 정제).
  - YAML 파싱 및 메인 스크래퍼 등록 목록 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20261003_add_teamblind_topic_best_portal/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20261003_add_teamblind_topic_best_portal/WALKTHROUGH.md)

---

### 21. Git 병합 충돌 및 GitHub 동기화 에러 수정
- **요청 일시**: 2026-10-06
- **요청 내용**: GitHub 원격 리포지토리(`origin/main`)와 로컬 `main` 브랜치 간 다이버전스 및 병합 충돌(`rss_scraper.py`, `.DS_Store`) 에러 해결.
- **처리 내역**:
  - `git pull --rebase` 실행 중 발생한 `.DS_Store` 파일 삭제 충돌 및 `rss_scraper.py` WAF 우회 로직 병합 충돌 해결.
  - `rss_scraper.py`: `curl_cffi` Chrome 임퍼소네이션과 Google FeedFetcher UA + `httpx` 비검증 2단계 폴백 구조로 선형 통합.
  - 리베이스 완료 후 `python3 src/main.py` 실행하여 포털/RSS 전체 수집 및 구글 스프레드시트 덮어쓰기 연동 동작 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20261006_github_error_fix/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20261006_github_error_fix/WALKTHROUGH.md)

---

### 22. 기사 본문(초반 300자) 스크랩 및 구글 시트 20개 단위 분할 저장
- **요청 일시**: 2026-10-06
- **요청 내용**: 기사 본문 글의 초반 300자 정도를 수집/정제하도록 개선하고, 구글 스프레드시트에 작성할 때 20개 기사 단위로 빈 행(빈칸)을 삽입하여 저장.
- **처리 내역**:
  - `rss_scraper.py`: 피드 `summary`/`description` 내 HTML 태그 수거 및 공백 정제 처리 후 300자 본문 세팅.
  - `google_sheets_exporter.py`: `_clean_body_text()` 헬퍼 구현 및 `"본문 (초반 300자)"` 시트 열 추가.
  - `google_sheets_exporter.py`: 20개 기사마다 1개의 빈 행(`[""] * 8`)을 삽입하여 구글 시트에 덮어쓰도록 내보내기 로직 구현.
  - `python3 src/main.py` 실행하여 총 737개 기사 수집 및 구글 시트 20개 단위 분할 저장 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20261006_extract_body_300chars_and_sheet_20row_chunks/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20261006_extract_body_300chars_and_sheet_20row_chunks/WALKTHROUGH.md)

---

### 23. 구글 시트 출처별 출력 순서 재정렬 (포모스/블라인드 최상위, 정부정책 최하단)
- **요청 일시**: 2026-10-06
- **요청 내용**: 포모스 및 블라인드 커뮤니티 글을 구글 스프레드시트 최상단에 배치하고, 언론사 RSS 뉴스는 중간, 정부 정책 데이터를 가장 하단에 위치하도록 정렬.
- **처리 내역**:
  - `google_sheets_exporter.py`: `_get_article_priority()` 헬퍼 구현 (1순위: 포모스/블라인드, 2순위: RSS 뉴스, 3순위: 정부/공공 정책).
  - `google_sheets_exporter.py`: `export()` 내 2중 정렬(우선순위 그룹 -> 발행일시 내림차순) 적용 후 20개 단위 빈 행 분할 덮어쓰기 완료.
  - `python3 src/main.py` 실행하여 총 754개 기사 수집 및 시트 상단(포모스/블라인드) - 중간(뉴스) - 하단(정부정책) 정렬 반영 검증 완료.
- **상태**: `완료 (Done)`
- **상세 이력 문서**:
  - 📄 [구현 계획서](docs/history/20261006_reorder_sheet_rows_community_top_govt_bottom/IMPLEMENTATION_PLAN.md)
  - 📄 [결과 보고서 (Walkthrough)](docs/history/20261006_reorder_sheet_rows_community_top_govt_bottom/WALKTHROUGH.md)




