# Календарь звонков

Веб-приложение для бронирования звонков. Владелец календаря создаёт типы событий
и просматривает предстоящие встречи; гость выбирает тип события, свободный слот
на ближайшие 14 дней и создаёт бронирование без регистрации.

## Публичное приложение

Развёрнутая версия на Render: https://python-project-386-9j4p.onrender.com

> Демо-версия: данные в контейнере эфемерные, типы событий добавляются
> через админку `/admin/event-types` или командой `flask seed`.

## Установка и запуск

Требования: Python 3.12, Poetry, Node.js 20+.

### Бэкенд (JSON API + HTML-страницы)

```bash
make install        # установка зависимостей и создание venv (poetry install)
make seed           # демо-типы событий
make dev            # dev-сервер: http://127.0.0.1:5000
```

### Фронтенд (SPA на React + Vite)

```bash
make frontend-install   # cd frontend && npm install
make frontend-dev       # dev-сервер: http://localhost:5173
```

### Docker

В корне репозитория лежит `Dockerfile` — по нему собирается образ и запускается
приложение (бэкенд Flask под Gunicorn):

```bash
make docker-build       # docker build -t call-calendar .
make docker-run         # docker run ... -e PORT=8080 -p 8080:8080 call-calendar
```

При старте контейнера приложение автоматически слушает порт из переменной
окружения `PORT` (по умолчанию 5000) на адресе `0.0.0.0`. Эта же переменная
используется при деплое: платформа назначает порт и выдаёт приложению
публичную ссылку.

Фронтенд — отдельная часть приложения: получает данные и выполняет действия
только через JSON API по контракту (`openapi/openapi.yaml`). CORS включён,
поэтому фронтенд корректно работает с отдельно запущенным бэкендом. Если бэкенд
поднят не на `http://127.0.0.1:5000`, задайте адрес через `VITE_API_URL` при
запуске фронтенда.

Страницы (HTML-версия бэкенда):

- `/` — виды брони (гость), выбор слота и бронирование без регистрации
- `/admin/event-types` — типы событий (владелец)
- `/admin/bookings` — предстоящие встречи всех типов (владелец)

Те же сценарии доступны через JSON API по контракту: `GET /event-types`,
`GET /event-types/{id}`, `GET /event-types/{id}/slots`, `POST /bookings`,
`GET /bookings/{id}`, `GET|POST /admin/event-types`, `GET /admin/bookings/upcoming`.

Правила бронирования: слоты формируются на 14 дней от текущей даты, будни
09:00–18:00, шаг 30 минут. На одно время нельзя создать две записи — даже для
разных типов событий.

## Проверка

```bash
make test           # pytest
make lint           # ruff
npm run e2e         # Playwright: <frontend/e2e>, поднимает Flask + SPA
docker build -t call-calendar . && docker run --rm -e PORT=5000 -p 5000:5000 call-calendar   # проверка образа
```

## Документация

- [Доменная модель](docs/domain.md) — сущности и сценарии владельца и гостя
- [API-контракт](docs/contract.md) — покрытие сценариев операциями API
- [Пользовательские сценарии](docs/scenarios.md) — сценарии для проверки и их покрытие E2E/pytest
- [OpenAPI-спецификация](openapi/openapi.yaml) — сгенерирована из TypeSpec (`typespec/`)

### Hexlet tests and linter status:
[![Actions Status](https://github.com/Vitalmet/python-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Vitalmet/python-project-386/actions)