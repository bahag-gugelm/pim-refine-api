# Dockerfile
FROM python:3.9

WORKDIR /opt/products_comp

#setting up the virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

#copying the project files
COPY . /opt/products_comp
RUN pip install -r requirements.txt

EXPOSE 8000

CMD exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
