FROM python:3.10-alpine

WORKDIR /github-slack-bot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
