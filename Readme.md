# Postgres

```python
--docker-compose.yaml--
  postgres:
    image: postgres:latest
    environment:
      - POSTGRES_DB=receipt_db
      - POSTGRES_USER=konno
      - POSTGRES_PASSWORD="receipt-$db%1"
    volumes:
      - db-receipt:/var/lib/postgresql/data
    ports:
      - "5432:5432"  #host port:container port(postgres)
    restart: always

.env file
DB_NAME=receipt_db
DB_USER=konno
DB_PASSWORD="receipt-$db%1"
DB_HOST=postgres   # or a Docker service name like "db"
DB_PORT=5432        # Default for PostgreSQL

settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME", ""),
        'USER': os.getenv("DB_USER", ""),
        'PASSWORD': os.getenv("DB_PASSWORD", ""),
        'HOST': os.getenv("DB_HOST", "postgres"),
        'PORT': os.getenv("DB_PORT", "5432"),
    }
}

# dump data
python manage.py dumpdata --natural-primary --natural-foreign --indent 2 > data.json

python manage.py dumpdata --exclude auth.permission --exclude contenttypes --natural-primary --natural-foreign --indent 2 > data.json

# Migrate Schema
python manage.py migrate

# Load Data into postgres
python manage.py loaddata data.json

#Backup Dump Data
python manage.py dumpdata --indent 2 > /mnt/nas/remanager/db/db_backups/db_backup_$(date +%F_%H-%M-%S).json

# Resotre data
python manage.py loaddata /mnt/nas/remanager/db/db_backups/db_backup_2025-09-24_15-12-30.json

docker cp ./data.json <コンテナID>:/receipt/data.json
docker cp ./data.json <container_id>:/receipt/data.json

```