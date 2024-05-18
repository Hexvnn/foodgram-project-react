# Foodgram

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

Проект доступен по адресу [foodgramproject.hopto.org](http://foodgramproject.hopto.org)

## Установка

1. Клонируйте репозиторий:

git@github.com:Hexvnn/foodgram-project-react.git

2. Перейдите в директорию проекта

cd foodgram-project-react

3. Установите зависимости

pip install -r requirements.txt


## Запуск с помощью Docker Compose

1. Убедитесь, что Docker и Docker Compose установлены на вашем компьютере.

2. Создать файл .env в папке проекта:

```plaintext
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с PostgreSQL
DB_NAME=django
POSTGRES_USER=django # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
DEBUG=0
```

3. Запустите проект с помощью Docker Compose:

docker-compose up -d

4. Список запущенных контейнеров доступен по команде:

docker-compose ps

5. Выполните миграции:

docker-compose exec backend python manage.py migrate

6. Загрузите статику

7. Заполните базу данных 

docker-compose exec backend python manage.py add_tags
docker-compose exec backend python manage.py add_ingredients  


## Автор

Богданов Семён


## Данные для проверки

host - foodgramproject.hopto.org;
admin: testuser;
password: 22332233;