# 개발 진행 및 요청 사항 기록 (REQUEST.md)

이 문서는 사용자가 요청한 개발 진행 관련 요청 사항과 처리 내역을 기록하는 파일입니다.

---

## 📋 요청 사항 기록 목록

### 1. Git 사용자 계정 설정 및 커밋 오류 해결
- **요청 일시**: 2026-09-09
- **요청 내용**: 깃 커밋 시 유저 정보 없어서 발생하는 오류 해결 및 계정 정보(`thshin81@naver.com`) 설정.
- **처리 내역**:
  - `git config user.name "thshin81"` 및 `git config user.email "thshin81@naver.com"` (글로벌/로컬) 설정
  - 기존 커밋 작성자 정보 `thshin81 <thshin81@naver.com>`으로 amend 완료
- **상태**: `완료 (Done)`

---

### 2. 요청 사항 기록용 REQUEST.md 파일 생성
- **요청 일시**: 2026-09-09
- **요청 내용**: 개발 진행에 관해 요청하는 사항들을 기록할 `REQUEST.md` 파일 생성 및 관리.
- **처리 내역**: `REQUEST.md` 파일 생성 및 이전/현재 요청 내역 정리 작성
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
- **처리 내역**: `pip freeze` 기반으로 주요 의존성 및 하위 의존성 라이브러리의 정확한 버전(pinned version)이 명시된 `requirements.txt` 파일 생성 완료
- **상태**: `완료 (Done)`

---

### 5. 블로그 주제 선정용 수집 프로그램 구축 및 구글 스프레드시트 연동
- **요청 일시**: 2026-09-09
- **요청 내용**: `config` 내 `feeds.yaml`, `keywords.yaml`, `portal.yaml`을 활용한 RSS 및 사이트 크롤링 뉴스 수집 엔진 구축 및 구글 스프레드시트 연동.
- **처리 내역**:
  - `rss_scraper.py` (피드당 최대 20개 수집) 및 `portal_scraper.py` 구현
  - `keywords.yaml` 기반 키워드 태그 및 카테고리 자동 분류 파이프라인 적용
  - `google_sheets_exporter.py` 구현 (덮어쓰기 모드 및 지정된 서비스 계정 키/스프레드시트 ID 연동)
  - CLI 명령어 분리 (`python src/main.py run-rss`, `python src/main.py run-portal`, `python src/main.py run-all`)
- **상태**: `완료 (Done)`




