FROM python:3.9.5-alpine

WORKDIR /usr/projects/swipe/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

#install psycopg2 dependencies
RUN apk update \
    && apk add --virtual build-deps libffi-dev gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del build-deps

#after installation fill db with sql dump
# sudo docker exec -i {DB_CONTAINER} psql -U {DB_USER_NAME} -d {DB_NAME} < {BACKUP_FILE}

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/projects/swipe/src/entrypoint.sh"]