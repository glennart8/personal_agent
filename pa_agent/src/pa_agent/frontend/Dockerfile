# install python 3.12, slim is for installing a smaller python with less preinstalled packages
FROM python:3.12-slim

# root folder
WORKDIR /app

# copy frontend folder to working dir
COPY frontend .


# RUN = runs commands while building the image 

# install uv
RUN pip install --no-cache-dir uv

# install dependencies
RUN uv sync --no-dev

# installera ljuddrivrutin till linux
RUN apt-get update && apt-get install -y \
libportaudio2 \
&& rm -rf /var/lib/apt/lists/*


# CMD = the command that will be executed when starting the container

# run streamlit app and specify port and address
CMD ["sh", "-c", "uv run streamlit run app.py \ 
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0"]