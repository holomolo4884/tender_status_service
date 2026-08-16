# Tender Status Service

Микросервис трекинга статуса тендеров на Python (Django + DRF).

Сервис позволяет создавать тендеры, переводить их между статусами
и ведёт неизменяемую историю каждого изменения статуса
(кто изменил, когда и почему).

## Возможности

- Создание тендера (начальный статус — `Черновик`)
- Обновление статуса по конечному автомату:
  `Черновик → Активен → Выигран / Проигран`
- Аудит-лог каждого изменения статуса в отдельной таблице
- Валидация допустимых переходов
- REST API с кодами 404 / 409 / 422

## Стек технологий

- Python 3.12+
- Django 5.x
- Django REST Framework
- SQLite (разработка) / PostgreSQL (продакшн)
- pytest, pytest-django

## Структура проекта

```
tender_service/
├── config/                 # настройки проекта
│   ├── settings.py
│   └── urls.py
├── tenders/                # приложение тендеров
│   ├── constants.py        # статусы и матрица переходов
│   ├── models.py           # Tender, TenderStatusHistory
│   ├── services.py         # бизнес-логика
│   ├── serializers.py      # схемы запросов/ответов
│   ├── views.py            # эндпоинты
│   ├── exception_handlers.py
│   ├── urls.py
│   └── tests/
├── docs/                   # документация
│   └── SOLUTION.md         # логика решения и алгоритм
├── manage.py
├── requirements.txt
├── LICENSE
└── README.md
```

## Быстрый старт

```bash
# клонировать репозиторий
git clone <url-репозитория>
cd tender_service

# создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# установить зависимости
pip install -r requirements.txt

# применить миграции
python manage.py migrate

# запустить сервер
python manage.py runserver
```

Сервис доступен на `http://127.0.0.1:8000`.

## API

Базовый префикс: `/api/v1`.

| Метод   | Путь                           | Описание                      | Коды               |
|---------|--------------------------------|-------------------------------|--------------------|
| POST    | `/api/v1/tenders/`             | Создать тендер                | 201, 422           |
| GET     | `/api/v1/tenders/{id}/`        | Детали тендера                | 200, 404           |
| PATCH   | `/api/v1/tenders/{id}/status/` | Обновить статус               | 200, 404, 409, 422 |
| GET     | `/api/v1/tenders/{id}/history/`| История изменений статуса     | 200, 404           |

### Примеры запросов

**Создать тендер:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/tenders/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Тендер 1", "description": "Описание"}'
```

**Сменить статус:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/tenders/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "ACTIVE", "changed_by": "ivan", "reason": "Опубликован"}'
```

**Получить историю:**
```bash
curl http://127.0.0.1:8000/api/v1/tenders/1/history/
```

### Коды ошибок

| Код | Значение                                        |
|-----|-------------------------------------------------|
| 404 | Тендер не найден                                |
| 409 | Недопустимый переход статуса                    |
| 422 | Ошибка валидации (нет `reason`, неверный статус)|

## Статусы и переходы

| Статус   | Код     | Описание                             |
|----------|---------|--------------------------------------|
| Черновик | `DRAFT` | Начальное состояние при создании     |
| Активен  | `ACTIVE`| Тендер опубликован                   |
| Выигран  | `WON`   | Терминальное состояние               |
| Проигран | `LOST`  | Терминальное состояние               |

Допустимые переходы: `DRAFT → ACTIVE → WON | LOST`.
Подробнее — в [docs/SOLUTION.md](docs/SOLUTION.md).

## Тесты

```bash
pytest
```

## Лицензия

[MIT](LICENSE)
