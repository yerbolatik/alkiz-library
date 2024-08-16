# Django project

This project is bootstrapped using [fandsdev/django](http://github.com/fandsdev/django) template. [Drop a line](https://github.com/fandsdev/django/issues) if you have some issues.

## Project structure

The main django app is called `app`. It contains `.env` file for django-environ. For examples see `src/app/.env.ci`. Here are some useful app-wide tools:

- `app.admin` — app-wide django-admin customizations (empty yet), check out usage [examples](https://github.com/fandsdev/django/tree/master/%7B%7Bcookiecutter.name%7D%7D/src/app/admin)
- `app.test.api_client` (available as `api` and `anon` fixtures within pytest) — a [convenient DRF test client](https://github.com/fandsdev/django/blob/master/%7B%7Bcookiecutter.name%7D%7D/src/users/tests/tests_whoami.py#L6-L16).

Django user model is located in the separate `users` app.

Also, feel free to add as many django apps as you want.

## Installing on a local machine

This project requires python 3.11. Deps are managed by [poetry](https://python-poetry.org).

Install requirements:

```bash
poetry install
```
