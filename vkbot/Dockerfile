FROM python:3.10.4

WORKDIR /vkbot

COPY ./requirements.txt /vkbot/requirements.txt
COPY ./start_message.txt /vkbot/start_message.txt

RUN pip install --no-cache-dir --upgrade -r /vkbot/requirements.txt

COPY ./main.py /vkbot/main.py

CMD ["python", "-u", "main.py"]