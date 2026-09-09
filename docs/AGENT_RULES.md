# 🤖 AI Agent 작업 지침 및 프로젝트 규칙 (AGENT_RULES)

이 문서는 AI 작업자(Agent)가 본 프로젝트(`topic_scroll`)에서 개발 작업을 수행할 때 **반드시 준수해야 하는 필수 작업 규칙**입니다.

---

## 🚨 필수 작업 규칙 (Mandatory Rules)

### 1. Git 자동 커밋 절대 금지 🚫
- 사용자가 대화에서 명시적으로 `git commit`을 요청하기 전까지는 **절대로 `git commit`을 자동 실행하지 않습니다.**
- 파일 수정 및 생성은 수행하되, Git 커밋은 항상 사용자가 직접 진행하거나 explicit 요청 시에만 수행합니다.

### 2. 요청 사항 이력 기록 (`REQUEST.md`) 📝
- 사용자가 전달하는 모든 개발 진행 요청 사항은 프로젝트 루트의 **[REQUEST.md](file:///app/REQUEST.md)** 파일에 일시, 내용, 처리 내역, 상태를 누적하여 기록합니다.

### 3. 세부 이력 문서화 (`docs/history/`) 📁
- 모든 기능 개발 및 요청건 완료 시 **`docs/history/YYYYMMDD_<작업주제>/`** 디렉터리를 생성하고 아래 두 문서를 저장한 후 `REQUEST.md`에 링크를 연결합니다.
  - `IMPLEMENTATION_PLAN.md`: 요구사항, 변경 설계, 검증 계획
  - `WALKTHROUGH.md`: 구현 완료 내역, 테스트 명령어, 연동 결과

### 4. 실환경 의존성 동기화 (`requirements.txt`) 📦
- 새로운 신규 라이브러리 설치 시 `requirements.txt`에 정확한 버전(Pinning)을 등록하여 실환경 배포 호환성을 유지합니다.
