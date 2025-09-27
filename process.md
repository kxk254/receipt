py .\manage.py collectstatic 

docker compose up --d

docker compose down

docker compose ps
docker ps -a  ## check if crashed or not

docker compose restart

docker stop nginx app
docker rm nginx app
docker rmi nginx:latest remanager_v11-app

scp -r ./receipts kenji-konno@100.94.246.4:/home/kenji-konno/

ssh kenji-konno@100.94.246.4

move to the directory....
docker build -t receipts:latest .

docker run -d -p 8901:8000 receipts:latest

### Yaml file
docker compose up -d --build

http://100.94.246.4:8901

### Migration
docker exec youthful_roentgen python manage.py migrate


###  recreate

stop and remove container

docker rm container name
docker system prune

cp /mnt/nas/develop/receipt/receipt202505dep/receipts/db.sqlite3 /var/lib/docker/volumes/receipts_db-vol/_data

python db_backup_gui.py

COMPOSE_PROJECT_NAME=receipts docker compose up -d

volume -----
docker volume ls
docker volume rm static-receipt db-receipt
docker volume prune

 docker image rmi receipts-receipt:latest nginx:latest 

 Add to groupadd sharedapps-----
 sudo groupadd sharedapps
 getent group sharedapps
 sudo groupadd -g 1001 sharedapps
 sudo usermod -aG sharedapps username

 ---Migrate
 docker exec -it <containername> bash
 python manage.py migrate

-- remove images and volume
 docker compose down --rmi all -v

6bcaf2962bfb