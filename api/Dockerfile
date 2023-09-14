FROM python:3.10.4

WORKDIR /api

ARG DB_NAME
ENV DB_NAME=$DB_NAME

COPY ./requirements.txt /api/requirements.txt
COPY ./${DB_NAME} /api/${DB_NAME}

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./app /api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
