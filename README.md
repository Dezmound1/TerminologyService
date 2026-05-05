# Сервис терминологии

REST-сервис справочников. Хранит коды и значения терминов (например, специальности медработников, МКБ-10), позволяет получать списки справочников и их версий, проверять наличие конкретного элемента в указанной версии.

Реализован как тестовое задание. Бизнес-описание - в [TASK.md](TASK.md)
## Quick start

### Подготовка

1. Установить [Task](https://taskfile.dev/) (раннер команд) - инструкция в [TASK_INSTALL.md](TASK_INSTALL.md).
2. Установить Docker и Docker Compose.
3. Клонировать репозиторий и создать `.env` из примера:

```bash
git clone https://github.com/Dezmound1/TerminologyService.git
cd TerminologyService
cp .env.example .env
```

### Запуск

```bash
task build
task up
```

Будут подняты PostgreSQL и Django (порт 8000). При первом старте автоматически применяются миграции и создаётся суперпользователь (логин/пароль из `.env`, по умолчанию `admin/admin`).

После запуска доступны:

- API - http://localhost:8000/api/refbooks/
- Swagger - http://localhost:8000/api/schema/swagger-ui/
- Админка - http://localhost:8000/admin/

### Остановка

```bash
task down
```

## Команды Task

```bash
task --list-all
```

Основные:

| Команда | Описание |
|---|---|
| `task up` / `task down` | Поднять / остановить контейнеры |
| `task migrate` | Применить миграции |
| `task test` | Все тесты (нужен поднятый postgres) |
| `task test-unit` | Только юнит-тесты (без БД) |
| `task lint` / `task format` | Ruff |
| `task type-check` | basedpyright |

## API

Все эндпоинты - `GET`, возвращают JSON.

### `GET /api/refbooks/[?date=YYYY-MM-DD]`

Список справочников. Без параметра - все. С `date` - только те, у которых есть версия с датой начала действия не позже указанной.

```json
{
  "refbooks": [
    {"id": 1, "code": "MS1", "name": "Специальности медработников"},
    {"id": 2, "code": "ICD-10", "name": "МКБ-10"}
  ]
}
```

### `GET /api/refbooks/<id>/elements/[?version=X.Y]`

Элементы справочника. Без `version` - элементы текущей версии (та, у которой `start_date` максимальна, но не позже сегодняшней даты).

```json
{
  "elements": [
    {"code": "J00", "value": "Острый назофарингит"},
    {"code": "J01", "value": "Острый синусит"}
  ]
}
```

### `GET /api/refbooks/<id>/check_element/?code=...&value=...[&version=...]`

Проверка наличия элемента. Возвращает `{"exists": true}` или `{"exists": false}` со статусом 200 в любом случае. 404 возвращается только если справочник или указанная явно версия не существуют.

## Архитектура

Проект разделён на два пакета:

- **`core/`** - проектный пакет: settings, корневые URL, WSGI/ASGI. Только композиция, без бизнес-логики.
- **`refbooks/`** - Django-app, bounded context справочников. Внутри - луковая структура:

```
refbooks/
├── domain/         # frozen dataclass-ы и доменные исключения, без зависимостей
├── models.py       # Django ORM
├── admin.py        # Django Admin
├── repositories/   # доступ к ORM, возвращают доменные сущности
├── services/       # бизнес-логика, оркестрация
└── api/            # DRF views, сериализаторы, URL-ы
```

Правила импортов: `domain/` ничего не знает о Django, `services/` не лезет в `models.py` напрямую, `api/` не лезет в `repositories/`.

### Почему так

**Repository ↔ Service.** Репозиторий - чистый data access (один SQL-запрос на метод, возвращает entity). Сервис - оркестрация и бизнес-правила. Например, правило «если версия не указана - берём текущую» живёт в `ElementService._resolve_version_id`, репозиторий ничего не знает о «сегодня».

**Domain entities (frozen dataclass).** ORM-модели остаются внутри `models.py` и `repositories/`. Сервисы и API работают с иммутабельными dataclass-ами - их легко создать в тестах, не дёргая БД.

## Тесты

```bash
task test           # все тесты внутри контейнера
task test-unit      # юнит-тесты локально, без БД
```

Юнит-тесты сервисов работают через моки репозиториев (БД не нужна). Интеграционные тесты API используют `pytest-django` и реальный PostgreSQL. Покрытие - 95%, требование `>=80%` зашито в `pyproject.toml`.

## Стек

- Python ≥ 3.10, Django 4.2 LTS, DRF 3.14+
- PostgreSQL 16
- uv (менеджер пакетов), ruff (линтер/форматтер), basedpyright (type checker)
- pytest, pytest-django, pytest-cov
- drf-spectacular (Swagger)

## Переменные окружения

Файл `.env` (см. `.env.example`):

| Переменная | Описание | По умолчанию |
|---|---|---|
| `POSTGRES_USER` | Пользователь БД | `refbook` |
| `POSTGRES_PASSWORD` | Пароль БД | `refbook` |
| `POSTGRES_HOST` | Хост БД (`postgres` в Docker, `localhost` локально) | `postgres` |
| `POSTGRES_DB` | Имя БД | `refbook` |
| `POSTGRES_PORT` | Порт БД | `5432` |
| `DJANGO_SECRET_KEY` | Секретный ключ Django | - |
| `DJANGO_DEBUG` | Режим отладки | `True` |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты (через запятую) | `localhost,127.0.0.1` |
| `DJANGO_SUPERUSER_USERNAME` | Логин суперюзера (создаётся при старте) | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Email суперюзера | `admin@example.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Пароль суперюзера | `admin` |
