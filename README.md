# Django news blog

## Setup

1. add .env.local file in root dir

2. start database with server:

```bash
docker-compose --env-file ./.env.local up -d
```

> Seeing console output 
```bash
docker-compose logs --follow backend
```

> If you would like start project locally:
  ```bash
  # stop docker container instance with project
  docker-compose stop backend
  # create virtualenv
  python3 -m venv venv 
  # apply envs
  source ./.env.local
  # start server
  python server/manage.py runserver
  ```
