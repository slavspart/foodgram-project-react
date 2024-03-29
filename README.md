# praktikum_new_diplom
[Описание](#описание) /

[Запуск](#запуск) /

[Документация](#документация)/

## Описание
Проект [foodgram](https://github.com/slavspart/foodgram-project-react) - аггрегатор рецептов. 
Пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Данный репозиторий предназначен для деплоя проекта на сервере в контейнерах Docker (контейнеры frontend(приложение на React), backend(приложение на Django), nginx, db(контейнер с PostgreSQL)) при помощи workflow. Проект для запуска на локальной машине - foodgram-containers](https://github.com/slavspart/foodgram-containers).

Проект состоит из фронтенда на фреймворке React, взаимодействующего с API-бэкендом, разработанном на Django.Бэкенд состоит из двух модулей:
  - **api**. Модуль для работы с рецептами.
  - **users**. Модуль для работы с пользователями.

Проект разработан:
  
  - **Бэкенд**:
*Cтудентом когорты 14+ курса Python разработчик + Яндекс практикума <a href="https://github.com/slavspart" target="_blank">Святославом Михайловым</a>.
  
  - **Фронтэнд**:
*Неизвестными героями :)) из  <a href="https://practicum.yandex.ru" target="_blank">Яндекс практикума</a>

## Запуск
git
``` 
сделать форк репозитория https://github.com/slavspart/foodgram-project-react

Настроить взаимодействие с Dockerhub (добавить в git secrets ключи DOCKER_USERNAME, DOCKER_PASSWORD)

Настроить взаимодействие с сервером (добавить в git secrets ключи HOST, USER, SSH_KEY, PASSPHRASE)

Добавить переменные окружения для работы (добавить в git secrets ключи SECRET_KEY, HOSTS, DB_ENGINE, DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT)
```
  
веб-сервер
```
Для запуска проекта необходимо подготовить веб-сервер:

Установить  докер:

- sudo apt install docker.io

Установить docker-compose

Скопировать в папку home/username/infra файл ngingx.conf и docker-compose.yml

```

git
``` 
Перейти в папку git actions.

Запустить fg_workflow
```

## Документация
После запуска документация доступна по адресу http://<your_server>/api/docs/redoc.html
