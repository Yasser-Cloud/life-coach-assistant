FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pipenv 

COPY data/daily_dialog.csv data/daily_dialog.csv
COPY ["Pipfile", "Pipfile.lock", "./"]


COPY life_coach .

RUN pipenv install --deploy --ignore-pipfile --system


CMD ["pipenv", "run", "streamlit", "run", "app.py"]  



