# Телеграм-бот "Кулинарная книга"

### Помимо стандартного поиска рецептов по категориям и ингредиентам, есть возможность ограничения по ингредиентам.

1. Перед запуском приложения необходимо создать файл .env, добавив в него 
собственные значения переменных окружения (указаны в файле .env_template): данные для регистрации суперпользователя и токен для telegram-бота.


2. Запуск Django-приложения осуществляется командой:
    ```
    docker-compose up
    ```


3. После запуска приложения доступна Swagger-документация: url /api/docs


4. Добавлять новые записи в модели можно через админку. Также реализовано добавления данных через импорт csv-файла (примеры файлов: categories.csv, ingredients.csv, recipes.csv).


5. Для запуска бота необходимо набрать команды:
    ```
    docker exec -it my_cookbook /bin/sh
    cd ../bot && python handlers.py
    ```
