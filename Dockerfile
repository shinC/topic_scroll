# 파이썬 3.14 베이스 이미지 사용
FROM python:3.14-slim AS base

# 파이썬 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 빌드 의존성 설치 (필요시)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 보안을 위한 non-root 사용자 생성
RUN groupadd -g 10001 appgroup && \
    useradd -u 10000 -g appgroup -s /bin/bash -m appuser

# 소스코드, 메타데이터 복사 및 패키지 설치
COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --no-cache-dir .

# 데이터 및 로그 디렉터리 생성 및 권한 설정
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appgroup /app

# non-root 사용자로 전환
USER appuser

# 기본 실행 엔트리포인트 설정
ENTRYPOINT ["python", "src/main.py"]
CMD ["--help"]

