# Социальная сеть

Автор: Молчан Егор, БПМИ 2110

## Запуск:

```docker-compose up --build```

Затем надо провести liquibase-миграцию. На данный момент делается отдельной командой, я не успел разобраться как провести это внутри Докера:

```docker run --rm --network="snet-network" -v "$(pwd)/main_service/migrations":/snet liquibase/liquibase:4.19.0 --defaultsFile=/snet/dev.properties update```

Сервис запускается по адресу ```localhost:8000```.

## Спецификация

Доступна по адресу ```localhost:8000/docs```

## Обзор

Регистрироваться можно по адресу ```localhost:8000/registry```, в ```body``` нужно предоставить поля ```login``` и ```password```.

После регистрации необходим вход по адресу ```localhost:8000/login``` в ```form-data``` нужно предоставить поля ```username``` и ```password```.

Залогиненый пользователь может поменять данные о себе, отправив на адрес ```localhost:8000/user/update``` запрос с какими-то из полей ```name```, ```surname```, ```birthdate```, ```email```, ```phone```.
