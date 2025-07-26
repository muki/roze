#! /bin/bash

# run things
docker-compose up -d

# after things are up start the tailwind server
docker-compose exec django python manage.py tailwind start

# on ctrl+c on the server stop everything
docker-compose stop
