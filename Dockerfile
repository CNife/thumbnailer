FROM python:3.12-slim

WORKDIR /code

COPY requirements.docker.txt ./
RUN pip install -r requirements.docker.txt --no-cache-dir && \
    rm requirements.docker.txt

COPY src ./

ENTRYPOINT ["python", "-u", "-m", "video_thumbnail"]