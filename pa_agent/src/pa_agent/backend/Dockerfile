# install python 3.12, slim is for installing a smaller python with less preinstalled packages
FROM python:3.12-slim

# root folder
WORKDIR /app

# copy data, knowledge_base and backend to root folder with same folder names
# /app/data, /app/knowledge_base etc
COPY data data
COPY knowledge_base knowledge_base
COPY backend backend

# switch working dir to backend folder (cd /app/backend)
WORKDIR /app/backend

# here we install uv with pip (pip is installed with python)
RUN pip install --no-cache-dir uv

# sync dependencies
RUN uv sync --no-dev

# run command for starting api when starting the container, specify host and port
CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
