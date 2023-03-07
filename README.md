# Foodgram - Продуктовый помошник помощник
 

На этом сервисе пользователи могут публиковать кулинарные рецепты, подписываться 
публикации других пользователей, добавлять понравившиеся рецепты в список 
«Избранное», а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

# Описание

Это готовый Docker-образ, содержащий REST API бекэнд и SPA-фронтенд на React. 
Пользователи могут:
- регистрироваться в приложении;
- получать токен для полноценного доступа к сайту;
- авторизованные пользователи могут создавать рецепты, добавлять их в избранное, подписываться на других пользователей, добавлять рецепты в список покупок;
- администраторы через специальный интерфейс могут создавать новых пользователей, изменять учетные данные других пользователей, редактировать ингредиенты, теги, рецепты;
- пользователи могут фильтровать рецепты по тегам, авторам.

----
[Сайт приложения Foodgram](https://158.160.10.21/)

- логин: ``
- пароль: `Pass2020!`

[Панель администратора](https://158.160.10.21/admin/)

- логин: `admin`
- пароль: `Pass2020!`
----

# ️ Установка и запуск

Для запуска приложения должен быть установлен [git](https://git-scm.com/) и [docker](https://www.docker.com/).

```bash
git clone git@github.com:egor-zhit/foodgram-project-react.git
cd foodgram-project-react
```

Шаблон для создания .env файла (содержит необходимые для работы перменные окружения). Данный файл должен находится в папке `infra` проекта:
```env
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Собрать и запустить контейнеры
```bash
cd infra
sudo docker-compose ud -d --build
```

После запуска контейнеров необходимо применить миграции, создать суперпользователя и собрать статику:
```bash
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```


Для наполнения базы данных данными можно использовать команду:

```bash
sudo docker-compose exec web python3 manage.py flush --no-input
sudo docker-compose exec web python3 manage.py loaddata fixtures.json
```

# Использованные технологии

- [Python 3.8](https://www.python.org/)
- [Django 3.2](https://www.djangoproject.com/)
- [Django Rest Framework 3.12](https://www.django-rest-framework.org/)
- [Djoser](https://djoser.readthedocs.io/en/latest/)
- [django-filter](https://github.com/carltongibson/django-filter/)
- [django-colorfield](https://pypi.org/project/django-colorfield/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [Docker](https://docker.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Nginx](https://www.nginx.com/)
    
# Лицензия

[MIT](https://choosealicense.com/licenses/mit/)

# Автор

- Егор Житников