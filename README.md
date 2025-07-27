# Rože

An app to help keep house plants alive.

Documentation is (obviously) lacking, but it's a Django app with Tailwind. Everything but WebPush notifications works with JavaScript disabled (a bit of a code golf challenge). Unsold on Tailwind, TBH, but maybe I'm holding it wrong. Running `docker compose up` should get everything running. You will need to migrate the database and create a superuser to do anything useful. Otherwise, it should "just work", except for things like notifications if you did not populate the settings correctly. Have a look at `docker-compose.override.yaml.example` and `base/settings_dev.py.example` for inspiration.

Huey is used to run tasks, at this point it's just notifications.

Nginx is there to make (self-hosted) deployment more pleasant when turning off debug mode.

It's small and single tennant right now, so we default to SQLite for everything, you can of course tweak the settings to use something else.

Currently the app always runs with `python manage.py runserver 0.0.0.0:8000` because, again, this is very local software. If you want to use gunicorn or something else edit the `requirements.txt` (to install things) and `docker-compose.override.yaml` (to change the command).

## Notifications

This part, like every other, is very much a work in progress.

### Gotify

If you have a Gotify instance you can use the settings and the code in `roze/tasks.py` to send notifications.

### Signal CLI REST API

If you have a Signal CLI REST API running you can use the settings and the code in `roze/tasks.py` to send notifications.

### WebPush

For WebPush we use [jazzband/django-push-notifications](https://github.com/jazzband/django-push-notifications/). These were the [instructions used](https://github.com/jazzband/django-push-notifications/blob/master/docs/WebPush.rst) for setting things up.

## Design

### Striving towards

- As little JavaScript as possible. Points for features that work with Javascript disabled.
- Accessibility (more of a TODO thing right now).
