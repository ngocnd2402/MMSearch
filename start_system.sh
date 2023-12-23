#!/bin/bash

# Tạo và chạy screen cho Frontend
screen -dmS aic_fe bash --login -c 'conda activate ngokrock; cd "/mmlabworkspace/Students/visedit/AIC2023/frontend"; npx next dev -p 8888; exec bash'

# Tạo và chạy screen cho Backend
screen -dmS aic_be bash --login -c 'conda activate ngokrock; python Backend/backend.py; exec bash'

# Tạo và chạy screen cho MeiliSearch
screen -dmS aic_meili bash --login -c 'conda activate ngokrock; cd "$(dirname "$0")"; ./meilisearch --db-path ./meilifiles --http-addr "localhost:5555"; exec bash'

echo "Các screen đã được tạo và chương trình đã được khởi chạy."
