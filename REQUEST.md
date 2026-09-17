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








