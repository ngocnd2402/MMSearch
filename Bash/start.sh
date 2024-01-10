# For the front-end service
screen -dmS aic_fe fish --login -c 'conda activate ngokrock; and cd "frontend"; and npx next dev -p 8888; and exec bash'

# For the back-end service
screen -dmS aic_be fish --login -c 'conda activate ngokrock; and python Backend/backend.py; and exec bash'

# For the MeiliSearch service
screen -dmS aic_meili fish --login -c 'conda activate ngokrock; and ./meilisearch --db-path ./meilifiles --http-addr "localhost:5555"; and exec bash'
