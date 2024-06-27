# 使用官方 Python 镜像作为基础镜像
FROM python:3.8-slim

# 安装 mediainfo
RUN apt-get update && apt-get install -y mediainfo

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到工作目录
COPY . /app

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 运行 Flask 应用
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
