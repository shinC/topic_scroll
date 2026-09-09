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

