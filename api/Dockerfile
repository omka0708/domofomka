FROM python:3.10.4

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt
COPY ./codes.db /api/codes.db

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./app /api/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
