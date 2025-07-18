# 1. Python 3.12.9 기반 이미지
FROM python:3.12.9-slim

# 2. Python 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 작업 디렉토리
WORKDIR /app

# 4. 필수 패키지 설치 (MySQL 클라이언트 포함)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic-dev \
    build-essential \
    curl \
    pkg-config \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Python 패키지 설치
COPY requirement.txt .
RUN pip install --upgrade pip
RUN pip install -r requirement.txt

# 6. 소스코드 복사
COPY . .

# 7. 컨테이너가 열 포트
EXPOSE 8000