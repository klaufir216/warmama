FROM tiangolo/meinheld-gunicorn:python3.8

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    python3-dev \
    build-essential \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --upgrade meinheld gunicorn \
    && pip install --no-cache-dir IPy \
    && pip install --no-cache-dir cheroot \
    && pip install --no-cache-dir pymysql \
    && pip install --no-cache-dir future

COPY ./src /app
COPY ./cgi.patch /tmp/

RUN patch /usr/local/lib/python3.8/cgi.py < /tmp/cgi.patch \
    && rm /tmp/cgi.patch

RUN cp -p /app/config-example.py /app/config-real.py

RUN mkdir -p /var/log/warmama/reports

ENV MODULE_NAME=wcgi
ENV VARIABLE_NAME=application
ENV WORKERS_PER_CORE=0.5
ENV WEB_CONCURRENCY=2
ENV PORT=9001

EXPOSE 9001