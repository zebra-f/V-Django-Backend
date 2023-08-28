
### How to run locally (Linux):  
(Tested on `Kubuntu 22.04`, `Python 3.10.6`, `Docker 24.0.5`.)
    
    $ # navigate to a desired directory
    $ git clone <project_url> 
    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ python3 manage.py migrate  

---
#### Environemnt variables:
Set up environment variables (generate a secure key for each variable name):  
   
    $ export DJANGO_V_ONE_SECRET_KEY=<secure_key_1>
    $ export MEILISEARCH_V_ONE_MASTER_KEY=<secure_key_2>
  
---
#### Meilisearch Docker container:
*(Meilisearch is not essential for running this application as a standalone REST API, If you wish to disable it and omit the rest of this paragraph edit the source code: `core/settings.py` and set the `disabled` key in the `MEILISEARCH` dictionary to `True`.  
Note that the model responsible for synchronizing data between the database and the search engine will still be created and updated.)*
  
Run an instance of Meilisearch in Docker, or refer to the Meilisearch documentation for other options.  
(Ensure to add `meili_data/` volume to the `.gitignore`, alternatively execute this command in a different directory suited for a storage).  

  
    $ sudo docker pull getmeili/meilisearch:v1.3
    $ # optionally, include `--rm`` flag
    $ sudo docker run -it --name ms_v_one -d -p 7700:7700 -e MEILI_MASTER_KEY=$MEILISEARCH_V_ONE_MASTER_KEY -v $(pwd)/meili_data:/meili_data getmeili/meilisearch:v1.3  
     
    $ # commands that create and update `speeds`, a Meilisearch index
    $ python3 manage.py createspeedsindex
    $ python3 manage.py updatespeedsindex


  

