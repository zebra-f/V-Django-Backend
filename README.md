Python version 3.10.6


How to run:   
  
set up environment variables:
DJANGO_V_ONE_SECRET_KEY,  
MEILISEARCH_V_ONE_MASTER_KEY,

Run an instance of Meilisearch in Docker, or refer to the documentation for other options.
(Ensure to add `meili_data/` volume to the `.gitignore`, alternatively execute this command in a different directory suited for storage).  

  
    $ sudo docker pull getmeili/meilisearch:v1.3
    $ sudo docker run -it --name ms_v_one -d -p 7700:7700 -e MEILI_MASTER_KEY='$MEILISEARCH_V_ONE_MASTER_KEY' -v $(pwd)/meili_data:/meili_data getmeili/meilisearch:v1.3


  

