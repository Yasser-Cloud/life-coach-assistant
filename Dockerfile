FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install pipenv

COPY data/daily_dialog.csv data/daily_dialog.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY life_coach .


CMD ["streamlit", "run", "app.py"]