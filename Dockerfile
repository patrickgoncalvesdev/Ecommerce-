FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ="America/Sao_Paulo"

WORKDIR /code

COPY requirements.txt /code/

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY . /code/

CMD [ "sh", "entrypoint.sh"]