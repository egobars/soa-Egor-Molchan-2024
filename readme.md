# Социальная сеть

Автор: Молчан Егор, БПМИ 2110

## Запуск:

```docker-compose up --build```

Сервис запускается по адресу ```localhost:8000```.

## Спецификация

Доступна по адресу ```localhost:8000/docs```

## Обзор

Регистрироваться можно по адресу ```localhost:8000/registry```, в ```body``` нужно предоставить поля ```login``` и ```password```.

После регистрации необходим вход по адресу ```localhost:8000/login``` в ```form-data``` нужно предоставить поля ```username``` и ```password```. Он вернёт Bearer-токен, который должен передаваться в ```Authorization``` хедере, например:

```Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkb2ciLCJleHAiOjE3MTAzNjQ2MTB9.IyvA5CCdSTcZTZJGZcdyN_KF00wgDpsOYhGugDDyN2Y```

Залогиненый пользователь может поменять данные о себе, отправив на адрес ```localhost:8000/user/update``` запрос с какими-то из полей ```name```, ```surname```, ```birthdate```, ```email```, ```phone```.
