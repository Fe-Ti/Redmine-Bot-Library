# Redmine-Bot-Library

###### (EN version of README.md is coming soon)

### Цель проекта

Цель Redmine-Bot-Library ‒ создать движок для реализации бота,
способного управлять системой Redmine.

### Текущее состояние
Проект находится в состоянии Proof-Of-Concept, т.е. он ещё не совсем
пригоден к использованию.

### Установка и запуск

1. Склонируйте репозиторий
2. Установите библиотеку [origamibot](https://github.com/cmd410/OrigamiBot)
3. Исправьте конфигурацию. На данный момент она находится в переменной `config`.
Параметры указанные ниже отвечают за соединение с сервером.
```python
    "use_https"             : False, # При False будет использован простой http
    "redmine_root_url"      : "localhost/redmine",
    "bot_user_key"          : "8e7a355d7f58e4b209b91d9d1f76f2a85ec4b0b6", # ключ API Redmine
```
4. Запустите test.py
```
python3 test.py [ключ бота в Telegram]
```


```
Copyright 2023 Fe-Ti aka T.Kravchenko
```
