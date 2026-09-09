# topic_scroll 📰

**`topic_scroll`**은 파이썬 3.14 기반의 고성능 비동기 뉴스 웹 스크래핑 엔진입니다. 다양한 뉴스/언론사 웹사이트의 기사 데이터를 비동기로 수집하고, 중복을 정제하여 원하는 포맷(JSON, JSONL, CSV)으로 저장할 수 있도록 설계되었습니다.

---

## 주요 특징 🚀

- **파이썬 3.14 기반**: 최신 파이썬 3.14 환경 지원 및 멀티스테이지 도커(Docker) 기반 실행 환경 구성.
- **비동기 HTTP 스크래핑**: `httpx` 및 `asyncio`를 활용하여 여러 뉴스 사이트를 동시에 빠르게 수집.
- **플러그인 아키텍처**: 추상 클래스(`BaseScraper`) 및 스크래퍼 레지스트리를 통한 간편한 신규 뉴스 사이트 추가.
- **데이터 자동 정제 및 중복 제거**: URL 및 기사 해시 기반의 중복 제거 파이프라인 탑재.
- **다양한 내보내기 지원**: JSON, JSONL, CSV 포맷 내보내기 지원.
- **편리한 CLI 인터페이스**: `typer` 기반의 직관적인 명령줄 도구 제공.

---

## 프로젝트 디렉터리 구조 📁

```
topic_scroll/
├── .env.example              # 환경 변수 설정 템플릿
├── .gitignore                # Git 관리 제외 항목
├── Dockerfile                # 파이썬 3.14 멀티스테이지 도커 빌드 파일
├── docker-compose.yml        # 도커 컨테이너 서비스 설정
├── pyproject.toml            # 프로젝트 의존성 및 패키지 설정
├── README.md                 # 프로젝트 가이드 문서 (본 파일)
├── docs/
│   └── DEVELOPER_GUIDE.md    # 신규 스크래퍼 개발 가이드 문서
└── src/                      # 소스코드 루트
    ├── main.py               # CLI 엔트리포인트
    ├── config.py             # 설정 관리 (Pydantic Settings)
    ├── models/               # 기사 및 수집 결과 데이터 모델
    │   └── article.py
    ├── scrapers/             # 스크래핑 코어 엔진 및 구현체
    │   ├── base.py           # 추상 스크래퍼 (BaseScraper)
    │   ├── registry.py       # 스크래퍼 자동 등록 및 레지스트리
    │   └── implementations/  # 사이트별 스크래퍼 모듈
    │       └── sample_news.py # 예시 스크래퍼 (해커뉴스 기준)
    ├── pipeline/             # 데이터 중복제거 및 내보내기
    │   ├── processor.py
    │   └── exporter.py
    └── utils/                # 공통 로거 및 비동기 HTTP 클라이언트
        ├── logger.py
        └── http_client.py
```

---

## 시작하기 🛠️

### 1. 도커(Docker / OrbStack)를 이용한 실행 (권장)

OrbStack 또는 Docker Desktop 환경이 설치되어 있는 경우 명령 한 줄로 간편하게 실행할 수 있습니다.

#### 등록된 스크래퍼 목록 확인
```bash
docker compose run --rm app list
```

#### 특정 스크래퍼 실행 (예: sample_news)
```bash
docker compose run --rm app run sample_news
```

#### 전체 스크래퍼 동시 수집 실행
```bash
docker compose run --rm app run-all
```

#### 저장 포맷 지정 실행 (CSV 저장 예시)
```bash
docker compose run --rm app run sample_news --format csv
```

수집된 기사는 호스트의 `./data/` 디렉터리에 자동으로 저장됩니다.

---

### 2. OrbStack / Dev Containers 개발 환경 활용

IDE(Antigravity / VS Code)에서 프로젝트를 개발할 때 **Dev Containers** 설정이 완료되어 있어, 호스트에 파이썬 3.14를 직접 설치하지 않고도 컨테이너 내부에서 바로 개발 및 디버깅을 진행할 수 있습니다.

1. IDE에서 `Reopen in Container` (또는 `Dev Containers: Reopen in Container`) 명령 실행
2. 컨테이너 내부 터미널에서 소스코드 수정 및 바로 CLI 실행 (`python src/main.py run sample_news`)

---

### 3. 로컬 파이썬 3.14 환경 실행


파이썬 3.14 환경이 로컬에 구축되어 있는 경우:

```bash
# 1. 의존성 설치
pip install -e .

# 2. 스크래퍼 목록 조회
python src/main.py list

# 3. 특정 스크래퍼 실행
python src/main.py run sample_news

# 4. 전체 스크래퍼 실행
python src/main.py run-all
```

---

## 환경 변수 설정 ⚙️

필요에 따라 `.env.example` 파일을 복사하여 `.env` 파일로 생성 후 설정을 변경할 수 있습니다.

```bash
cp .env.example .env
```

| 환경 변수 | 설명 | 기본값 |
| :--- | :--- | :--- |
| `APP_ENV` | 실행 환경 (`development`, `production`) | `development` |
| `LOG_LEVEL` | 로그 레벨 (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `DATA_DIR` | 결과 파일 저장 디렉터리 | `data` |
| `EXPORT_FORMAT` | 기본 내보내기 포맷 (`json`, `jsonl`, `csv`) | `json` |
| `REQUEST_TIMEOUT` | HTTP 요청 타임아웃 (초) | `15.0` |
| `MAX_CONCURRENT_REQUESTS` | 최대 비동기 동시 요청 수 | `5` |

---

## 신규 사이트 스크래퍼 추가 🧩

새로운 뉴스 사이트 스크래퍼를 추가하는 자세한 설명은 [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)를 참조하세요.

요약:
1. `src/scrapers/implementations/` 디렉터리에 신규 파이썬 파일(예: `my_news.py`)을 생성합니다.
2. `BaseScraper`를 상속받고 `@scraper_registry.register` 데코레이터를 붙입니다.
3. `name`, `site_name`, `base_url` 및 `parse()` 메서드를 구현하면 자동으로 등록되어 동작합니다.

---

## 라이선스 📄

MIT License
