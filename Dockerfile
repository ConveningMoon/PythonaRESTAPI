FROM python:3.7

WORKDIR /app

COPY requirements.txt .

RUN apt update
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]