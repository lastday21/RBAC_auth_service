# RBAC Auth Service

Сервис на FastAPI с аутентификацией по JWT и авторизацией по RBAC (Role Based Access Control).
Идея - после логина пользователь ходит с Bearer-токеном, а доступ к ресурсам определяется ролями и правилами в БД.

## Возможности

### Auth
- `POST /auth/register` - регистрация
- `POST /auth/login` - логин, выдача access token
- `POST /auth/logout` - логаут (токен отзывается через таблицу revoked tokens)

### Users
- `GET /users/me` - профиль текущего пользователя
- `PATCH /users/me` - обновление профиля (email, full_name)
- `DELETE /users/me` - soft delete (помечает пользователя неактивным)

### RBAC
- Роли, ресурсы (business elements), правила доступа (create/read/update/delete)
- Поддержка "own" и "all" (например read только своих объектов или read всех)
- Ответы:
  - `401` если нет токена / токен невалидный / токен отозван / пользователь неактивен
  - `403` если токен валиден, но прав не хватает

### Admin API и mock API
В проекте есть админские ручки для управления RBAC-сущностями и mock-ручки для демонстрации защиты ресурсов.
Актуальный список эндпоинтов смотри в Swagger: `/docs`.


## Стек

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL (для запуска) + SQLite (в unit тестах)
- Pytest, mypy, ruff, pre-commit, GitHub Actions

---

## Быстрый старт

### 1) Переменные окружения

Создай файл `.env` в корне проекта:

```env
APP_ENV=dev
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/postgres

JWT_SECRET=something_token
JWT_ACCESS_TTL_MINUTES=30
```

### 2) Поднять PostgreSQL

Вариант через Docker compose:


```bash
docker compose up -d db
```

### 3) Установка зависимостей

```bash
python -m venv .venv
# linux/mac:
#source .venv/bin/activate
# windows:
 .venv\Scripts\activate

pip install -r requirements.txt
```

### 4) Запуск приложения

```bash
uvicorn app.main:app --reload
```

Swagger:
- http://127.0.0.1:8000/docs

---

## Демо-данные (generate_demo_data)

Чтобы быстро получить готовые роли/ресурсы/правила и тестовых пользователей, засидь базу скриптом демо-данных.

Из корня проекта:

```bash
python -m app.db.generate_demo_data
```

После запуска в базе появятся тестовые сущности RBAC и (обычно) несколько пользователей/ролей.
Логины и пароли смотри в самом `generate_demo_data`.

---

## Примеры запросов

### Регистрация

```bash
curl.exe `
  -X POST "http://127.0.0.1:8000/auth/register" `
  -H "accept: application/json" `
  -H "Content-Type: application/json" `
  --data-raw "{`"full_name`":`"timur`",`"email`":`"timur@ti`",`"password`":`"1`",`"password_confirm`":`"1`"}"
```

### Логин

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "timur@ti",
  "password": "1"
}'
```

Ответ содержит `access_token`. Дальше его нужно передавать так:

```bash
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <TOKEN>"
```

### Логаут

```bash
curl -X POST http://127.0.0.1:8000/auth/logout \
  -H "Authorization: Bearer <TOKEN>"
```

После логаута токен считается отозванным и должен давать `401`.

---

## Тесты

Все тесты:

```bash
pytest -q
```

Unit тесты:

```bash
pytest -q -m "not integration"
```

Integration тесты:

```bash
pytest -q -m integration
```

---

## Линтеры и pre-commit

Установка хуков:

```bash
pre-commit install --install-hooks
```

Прогнать все проверки вручную:

```bash
pre-commit run -a
```

---

## CI

В GitHub Actions прогоняются:
- pre-commit
- mypy
- pytest

---

## Структура проекта

- `app/main.py` - создание FastAPI приложения, подключение роутеров
- `app/api/*` - роутеры (auth/users/admin/mock)
- `app/core/*` - JWT, auth, RBAC
- `app/models/*` - SQLAlchemy модели
- `app/schemas/*` - Pydantic схемы
- `app/db/*` - engine/session/init_db
- `tests/*` - тесты
