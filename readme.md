# Product Information Refine Tool API

## How to run the app locally

````
$ docker-compose up -d --build
````

and go to http://localhost:8000/docs

## Development

- setup virtualenv for the local develpoment
- install the requirements
- make .env file with the following local config parameters
```
SERVER_NAME="pim_refine_tool"
SERVER_HOST="http://localhost:8000"
POSTGRES_SERVER="35.233.0.181"
POSTGRES_USER="user"
POSTGRES_PASSWORD="pass"
POSTGRES_DB="pim_refine_tool"
FIRST_SUPERUSER="admin@example.com"
FIRST_SUPERUSER_PASSWORD="password"
```

- if the app-container still runs, stop it to avoid hosts/IPs conflicts etc.
- start the app manually
````
$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
````
- rebuild app image to push your changes into the conainer
- use local postgres db

Always generate migrations after altering the db-schema,
migrations should be included into correspondent commit
````
$ alembic revision --autogenerate -m "changes msg"
````
Manually apply migrations (up to the latest)
````
$ alembic upgrade head
````

## How to run tests

````
$ docker-compose exec app python -m pytest app/tests
````
