FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# 使用模組化版本的應用 (推薦)
CMD ["python", "app_modular.py"]

# 如要使用原版本，請取消註解下行並註解上行
# CMD ["python", "app.py"]