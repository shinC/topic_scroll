# [Implementation Plan] OrbStack Dev Container 환경 설정 (devcontainer.json)

- **작업 일시**: 2026-09-18
- **관련 요청**: OrbStack 및 VS Code Dev Containers 실행을 위한 `devcontainer.json` 설정 파일 생성

---

## 1. 개요 (Overview)

기존에 `.devcontainer/Dockerfile`은 작성되어 있었으나 `devcontainer.json` 설정 파일이 부재하여 OrbStack 및 VS Code Dev Containers 환경에서 컨테이너 기반 개발 환경 실행이 불가능했던 문제를 해결합니다.

---

## 2. 변경 설계 (Proposed Changes)

### `.devcontainer/devcontainer.json` [NEW]
- **빌드 설정**: `.devcontainer/Dockerfile` 참조 및 프로젝트 루트 context 설정
- **작업 디렉터리 및 마운트**: `/workspace` 바인드 마운트 연동
- **환경 변수**: `PYTHONPATH=/workspace/src` 설정
- **VS Code 설정**: Python 인터프리터 경로 및 Pylance 검색 경로(`/workspace/src`) 지정, 필수 확장자(`ms-python.python`, `ms-python.vscode-pylance`) 명시
- **생성 후 명령어**: `pip install -r requirements.txt` 자동 설치

---

## 3. 검증 계획 (Verification Plan)

- `.devcontainer/Dockerfile` 빌드 정상 완료 확인 (`docker build`).
- `devcontainer.json` JSON 포맷 유효성 검증.
- `REQUEST.md` 및 이력 문서 작성 및 규칙 준수 확인.
