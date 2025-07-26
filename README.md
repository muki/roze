# Rože

An app to help keep house plants alive.

Documentation is (obviously) lacking, but it's a Django app with Tailwind, no JavaScript in the browser just yet. Unsold on Tailwind, TBH, but maybe I'm holding it wrong. Running `docker compose up` should get everything running. You will need to migrate the database and create a superuser to do anything useful. Otherwise, it should "just work", except for things like notifications if you did not populate the settings correctly. Have a look at `docker-compose.override.yaml.example` and `base/settings_dev.py.example` for inspiration.

Huey is used to run tasks, at this point it's just notifications.

Nginx is there to make (self-hosted) deployment more pleasant when turning off debug mode.

It's small and single tennant right now, so we default to SQLite for everything, you can of course tweak the settings to use something else.

Currently the app always runs with `python manage.py runserver 0.0.0.0:8000` because, again, this is very local software. If you want to use gunicorn or something else edit the `requirements.txt` (to install things) and `docker-compose.override.yaml` (to change the command).
