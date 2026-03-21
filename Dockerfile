FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r github_repohunter/requirements.txt

EXPOSE 8000

CMD ["python", "github_repohunter/server.py"]
