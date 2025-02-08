# cloud_storage
Облачное хранилище (курсовая работа, третий курс)

## Запуск сервера

```bash
python3 server.py \
  --address=* --port=8080 \
  --dbname=galina --dbuser=galina --dbpassword=secret --dbschema=coursework \
  --storage=/var/lib/cloud_storage
# Database connected: (
#  'PostgreSQL 15.5 (Ubuntu 15.5-0ubuntu0.23.04.1) on x86_64-pc-linux-gnu,
#  compiled by gcc (Ubuntu 12.3.0-1ubuntu1~23.04) 12.3.0, 64-bit',)
# Running server at *:8080
^C
# Server stopped
# Database disconnected
```
