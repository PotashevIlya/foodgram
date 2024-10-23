### Workflow
[![Main Foodgram workflow](https://github.com/PotashevIlya/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/PotashevIlya/foodgram/actions/workflows/main.yml)

# Проект Foodgram
## Описание проекта
Foodgram - это сервис для публикации рецептов самых разнообразных блюд. Вы можете публиковать собственные рецепты, изучать рецепты других пользователей, подписываться на других пользователей, добавлять рецепты в избранное, добавлять рецепты в корзину, а перед походом в магазин скачать файлом список всех необходимых ингредиентов для покупки. 

## Как запустить проект в контейнерах
1. Клонировать репозиторий и перейти в него в командной строке
```
https://github.com/PotashevIlya/foodgram
```
```
cd foodgram
```
2. Создать .env файл в корневой директории по образцу .env.example
3. Запустить docker-compose
```
docker compose -f docker-compose.production.yml up
```
4. Применить миграции в контейнере бекэнда
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
5. Предзаполнить базу данных из csv-файлов - последовательно выполнить команды
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py fill_ingredients_from_csv
```
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py fill_tags_from_csv
```
6. Собрать статику бекэнда
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
7. Скопировать статику в директорию, связанную с volume
```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
8. Скопировать файлы спецификации API в директорию, связанную с volume
```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/docs/. /backend_static/static/redoc/
```
9. Создать суперпользователя (опционально)
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Как запустить проект локально (будет доступен только функционал API, без фронтенда)
1. Клонировать репозиторий и перейти в него в командной строке
```
https://github.com/PotashevIlya/foodgram
```
```
cd foodgram
```
2. Создать .env файл в корневой директории по образцу .env.example
3. Перейти в директорию бекенда
```
cd backend
```
4. Создать и активировать виртуальное окружение
```
python -m venv venv
```
```
source venv/Scripts/activate
```
5. Установить зависимости проекта
```
pip install -r requirements.txt
```
6. Выполнить миграции
```
python manage.py migrate
```
7. Предзаполнить базу данных из csv-файлов - последовательно выполнить команды
```
python manage.py fill_ingredients_from_csv
```
```
python manage.py fill_tags_from_csv
```
8. Создать суперпользователя (опционально)
```
python manage.py createsuperuser
```
9. Запустить проект
```
python manage.py runserver
```
## Доступные эндпоинты API:
- /api/users/ Get-запрос – получение списка пользователей. POST-запрос – регистрация нового пользователя. Доступно без токена.

- /api/users/{id} GET-запрос – персональная страница пользователя с указанным id (доступно без токена).

- /api/users/me/ GET-запрос – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям.

- /api/users/set_password POST-запрос – изменение собственного пароля. Доступно авторизированным пользователям.

- /api/auth/token/login/ POST-запрос – получение токена. 

- /api/auth/token/logout/ POST-запрос – удаление токена.

- /api/tags/ GET-запрос — получение списка всех тегов. Доступно без токена.

- /api/tags/{id} GET-запрос — получение информации о теге о его id. Доступно без токена.

- /api/ingredients/ GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента. Доступно без токена.

- /api/ingredients/{id}/ GET-запрос — получение информации об ингредиенте по его id. Доступно без токена.

- /api/recipes/ GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по имени автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

- /api/recipes/{id}/ GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

- /api/recipes/{id}/favorite/ POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей.

- /api/recipes/{id}/shopping_cart/ POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей.

- /api/recipes/download_shopping_cart/ GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей.

- /api/users/{id}/subscribe/ GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

- /api/users/subscriptions/ GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей.

Более подробно со спецификацией можно будет ознакомиться по ссылке /redoc/ после запуска проекта в контейнерах.

___
### Стек :bulb:
Django, Gunicorn, nginx, Rest API (DRF), PostgreSQL, Docker, CI/CD (GitHub Actions), React, Yandex Cloud.
___  
#### Автор проекта:    
:small_orange_diamond: [Поташев Илья](https://github.com/PotashevIlya)  
