FROM python:3.9-slim
RUN pip install pipenv
COPY . /app
WORKDIR /app
RUN pipenv install --system --deploy
ENTRYPOINT python run.py -c config/atomstroy.yaml -s stdout text telegram -i 10
