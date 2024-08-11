FROM python:3.8.12-slim

MAINTAINER sarath kumar sarath@psitrontech.com

RUN pip install pipenv

WORKDIR /app

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --system

COPY ["*.py", "project_one_model.pkl", "./"] 

EXPOSE 9696

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "predict:app"]