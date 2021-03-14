FROM python:3.9
WORKDIR /app
RUN pip install pipenv
COPY . /app
RUN pipenv install --system --deploy
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ['python', 'run.py']
