FROM alpine

RUN printf "https://dl-cdn.alpinelinux.org/alpine/edge/main\nhttps://dl-cdn.alpinelinux.org/alpine/edge/community\nhttps://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
    && mkdir -p /thermo/db \
    && apk add python3 uvicorn py3-sqlalchemy py3-sqlalchemy-utils py3-fastapi py3-starlette py3-greenlet py3-typing_inspect py3-aiosqlite \
            py3-email-validator py3-pydantic py3-pydantic-settings py3-annotated-types py3-anyio py3-click py3-dnspython py3-h11 \
            py3-idna py3-mypy-extensions py3-psutil py3-pydantic-core py3-dotenv py3-sniffio py3-typing-extensions \
    && rm -rf /var/cache/apk/*

COPY app /thermo/app
COPY main_fw.py /thermo/main_fw.py
WORKDIR /thermo/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
