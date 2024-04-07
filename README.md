### How to run with Docker:
(Make sure you're using the latest version of Docker that recognizes `docker compose` command instead of `docker-compose`,
otherwise, update `./compose/dev/composeup.sh` file.)  
    
    $ git clone <project_url>
    
---
#### Environemt variables:
Remove `boilerplate` prefix from these files `./compose/dev/django/boilerplate.env.dev` and `./boilerplate.env`, or
execute copy commands:  
    
    $ cp ./compose/dev/django/boilerplate.env.dev ./compose/dev/django/.env.dev
    $ cp ./boilerplate.env ./.env

After that fill in empty fields in `./compose/dev/django/.env.dev` and `./.env`.

---
#### Finally:  
    
    $ chmod +x start-project.sh
    $ ./start-project.sh
  
- - -
### How to run locally (Linux):  
(Two options, tested on `Kubuntu 22.04`, `Python 3.10.6`, `Docker 24.0.5`.)

    $ git clone <project_url>

    $ # Option 1
    $ # before running these commands set up environment variables,
    $ # PostgreSQL, Redis and/or Meilisearch by following instructions below starting at `Evironment variables:`
    $ chmod +x init-project.sh
    $ source ./init-project.sh
    $ ./start-project.sh local
    $ # in a seperate terminal
    $ celery -A core worker -B --loglevel=INFO 

    $ # Option 2
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ # and follow all the steps below

---
#### Environemnt variables:
Set up environment variables (generate a secure key/password for each variable name):  
   
    $ export MEILISEARCH_V_1_MASTER_KEY="<master-key>"
    $ export POSTGRES_V_1_PASSWORD="<password>"
    $ export DJANGO_V_1_SECRET_KEY="<secret-key>"

    $ export POSTGRES_DB_NAME="v_1"
    $ export DATABASE="postgres"

    $ export POSTGRES_HOST="127.0.0.1"
    $ export POSTGRES_PORT="5432"
    $ export POSTGRES_USER="postgres"
 
    $ export REDIS_HOST="127.0.0.1"
    $ export REDIS_PORT="6379"
    $ export REDIS_URL="redis://127.0.0.1:6379"

    $ export MEILISEARCH_DISABLED="1"
    # not required if MEILISEARCH_DISABLED is set to 1
    $ export MEILISEARCH_HOST="127.0.0.1v"
    $ export MEILISEARCH_PORT="7700"
    $ export MEILISEARCH_URL="http://meilisearch:7700"

    $ export DEBUG="1"

    $ ADMIN_URL_SEGMENT="test"

    $ export ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"
    $ export CORS_ALLOWED_ORIGINS="http://127.0.0.1:5173 http://localhost:5173"

    $ export CLIENT_BASE_URL="http://127.0.0.1:5173/"
    $ export ADMINS='[{"name": "Joe", "email": "joe@example.com"}, {"name": "Jane", "email": "jane@example.com"}]'

    $ export CLOUDFLARE_TURNSTILE_DISABLED="1"
    $ # not required if CLOUDFLARE_TURNSTILE_DISABLED is set to 1
    $ export CLOUDFLARE_TURNSTILE_TOKEN="<secret-token>"

    $ export GOOGLE_OAUTH_DISABLED="1"
    $ # not required if GOOGLE_OAUTH_DISABLED is set to 1
    $ export GOOGLE_OAUTH_CLIENT_SECRET=""
    $ export FRONTEND_CALLBACK_URL="http://127.0.0.1:5173/openid/googleredirect/"

---
#### Meilisearch Docker container:
*(Meilisearch is not essential for running this application as a standalone REST API, If you wish to disable it and omit the rest of this paragraph set `MEILISEARCH_DISABLED` `environemt variable` to `"1"`.  
  
Run an instance of Meilisearch in Docker, or refer to the Meilisearch documentation for other options.  
(Ensure to add `meili_data/` volume to the `.gitignore`, alternatively execute this command in a different directory suited for a storage).  
  
    $ sudo docker pull getmeili/meilisearch:v1.5
    $ # optionally, include --rm flag
    $ sudo docker run -it --name meilisearch-v-1-dev -d -p 7700:7700 -e MEILI_MASTER_KEY=$MEILISEARCH_V_1_MASTER_KEY -v $(pwd)/meili_data:/meili_data getmeili/meilisearch:v1.3  
     
    # don't run these commands if you're planning to use bash scripts (Option 1)
    $ # if MEILISEARCH_DISABLED is set to "0", run these commands that create and update `speeds`, a Meilisearch index
    $ python3 manage.py createspeedsindex
    $ python3 manage.py updatespeedsindex
  
---
#### PostgresSQL Docker container:  
  
Run an instance of PostgreSQL in Docker, or refer to the PostgreSQL documentation for other options.   
(Ensure to add `postgres/data` volume to the `.gitignore`, alternatively execute this command in a different directory suited for a storage).  
(To free up the port if PostgreSQL is already running on your system, you can use the following command: `$ sudo systemctl stop postgresql.service` or modify the port number in the command below, which will require a corresponding update in `environment variables` as well).

    $ sudo docker pull postgres:14.9  
    $ sudo docker run -itd -e POSTGRES_PASSWORD=$POSTGRES_V_1_PASSWORD -e POSTGRES_DB=v_1 -p 5432:5432 -v $(pwd)/postgres/data:/var/lib/postgresql/data --name postgres-v-1 postgres:14.9
    $ sudo docker exec -it postgres-v-1 createdb -U postgres v_1

    # don't run these commands if you're planning to use bash scripts (Option 1)
    $ python3 manage.py migrate
    $ python3 manage.py createsuperuser
    $ python3 manage.py createuser --sentinel deleted

---
#### Redis Docker container:
Run an instance of PostgreSQL in Docker, or refer to the Redis documentation for other options.  

    $ docker run --name redis-v-1-dev -p 6379:6379 -d redis:7.2.1-alpine

#### Finally (for Option 2):  

    $ python3 manage.py runserver
    $ # in a seperate terminal window
    $ celery -A core worker -B --loglevel=INFO 
