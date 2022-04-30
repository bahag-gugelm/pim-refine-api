# Dockerfile
FROM python:3.9

WORKDIR /opt/pim_refine_api

#setting up the virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

#copying the project files
COPY . /opt/pim_refine_api
RUN pip install -r requirements.txt

EXPOSE 8000

CMD exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
