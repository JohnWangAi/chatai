# 使用腾讯云镜像源的 Ubuntu 基础镜像
FROM ccr.ccs.tencentyun.com/library/ubuntu:20.04

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 配置 apt 源为腾讯云源
RUN sed -i 's/archive.ubuntu.com/mirrors.cloud.tencent.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.cloud.tencent.com/g' /etc/apt/sources.list

# 安装 Python 和依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.9 \
        python3.9-dev \
        python3.9-distutils \
        python3-pip \
        curl \
        && rm -rf /var/lib/apt/lists/* \
        && ln -s /usr/bin/python3.9 /usr/local/bin/python \
        && ln -s /usr/bin/python3.9 /usr/local/bin/python3 \
        && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
        python get-pip.py && \
        rm get-pip.py

# 配置 pip 使用腾讯云源
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.cloud.tencent.com && \
    pip install --no-cache-dir --upgrade pip

# 复制项目文件
COPY requirements.txt .
COPY app.py .
COPY templates ./templates

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"] 