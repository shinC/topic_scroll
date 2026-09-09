FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/workspace/src

WORKDIR /workspace

# 개발용 필수 패키지 및 git 설치 (OrbStack 환경용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 패키지 업그레이드
RUN pip install --upgrade pip setuptools wheel
