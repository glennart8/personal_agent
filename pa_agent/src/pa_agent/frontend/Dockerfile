FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install uv

RUN uv sync

# installera ljuddrivrutin till linux
RUN apt-get update && apt-get install -y \
libportaudio2 \
&& rm -rf /var/lib/apt/lists/*

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]