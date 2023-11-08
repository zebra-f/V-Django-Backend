
### How to run locally (Linux):  
(Tested on `Kubuntu 22.04`, `Python 3.10.6`, `Docker 24.0.5`.)
    
    $ # navigate to a desired directory
    $ git clone <project_url> 
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt

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
    $ export REDIS_URL="redis://redis:6379"

    $ export MEILISEARCH_HOST="127.0.0.1v"
    $ export MEILISEARCH_PORT="7700"
    $ export MEILISEARCH_URL="http://meilisearch:7700"
    $ export MEILISEARCH_DISABLED="1"

    $ export ALLOWED_HOSTS="localhost 127.0.0.1 [::1]"

    $ export DEBUG="1"

  
---
#### Meilisearch Docker container:
*(Meilisearch is not essential for running this application as a standalone REST API, If you wish to disable it and omit the rest of this paragraph set `MEILISEARCH_DISABLED` `environemt variable` to `"0"`.  
Note that the model responsible for synchronizing data between the database and the search engine will still be created and updated.)*
  
Run an instance of Meilisearch in Docker, or refer to the Meilisearch documentation for other options.  
(Ensure to add `meili_data/` volume to the `.gitignore`, alternatively execute this command in a different directory suited for a storage).  
  
    $ sudo docker pull getmeili/meilisearch:v1.3
    $ # optionally, include `--rm`` flag
    $ sudo docker run -it --name ms_v_one -d -p 7700:7700 -e MEILI_MASTER_KEY=$MEILISEARCH_V_1_MASTER_KEY -v $(pwd)/meili_data:/meili_data getmeili/meilisearch:v1.3  
     
    $ # commands that create and update `speeds`, a Meilisearch index
    $ python3 manage.py createspeedsindex
    $ python3 manage.py updatespeedsindex
  
---
#### PostgresSQL Docker container:  
  
Run an instance of PostgreSQL in Docker, or refer to the PostgreSQL documentation for other options.   
(Ensure to add `postgres/data` volume to the `.gitignore`, alternatively execute this command in a different directory suited for a storage).  
(To free up the port if PostgreSQL is already running on your system, you can use the following command: `$ sudo systemctl stop postgresql.service` or modify the port number in the command below, which will require a corresponding update in `environment variables` as well).

    $ sudo docker pull postgres:14.9  
    $ sudo docker run -itd -e POSTGRES_PASSWORD=$POSTGRES_V_1_PASSWORD -e POSTGRES_DB=v_1 -p 5432:5432 -v $(pwd)/postgres/data:/var/lib/postgresql/data --name postgres_v_1 postgres:14.9
    $ sudo docker exec -it postgres_v_1 createdb -U postgres v_1

    $ python3 manage.py migrate
    $ python3 manage.py createsuperuser
    $ python3 manage.py createuser --sentinel deleted
