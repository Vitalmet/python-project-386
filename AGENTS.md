# AGENTS.md

Инструкции для агентов (ИИ-ассистентов), работающих в этом проекте.

## Обзор проекта

Веб-приложение «Календарь звонков»: бэкенд на Flask 3 (Python 3.12) + SQLite
(JSON API и HTML-страницы), фронтенд — SPA на React 18 + Vite + TypeScript.
API-контракт зафиксирован в TypeSpec (`typespec/`) и компилируется в
`openapi/openapi.yaml`. Интеграционные тесты — Playwright (`frontend/e2e/`).

## Ключевые команды

### Бэкенд

```bash
make install      # poetry install
make dev          # flask --app calendar_app --debug run (http://127.0.0.1:5000)
make seed         # демо-типы событий
make docker-build # сборка образа
make docker-run   # запуск контейнера (порт из переменной PORT)
```

### Тестирование

```bash
make test         # poetry run pytest
npm run e2e       # Playwright (frontend/e2e, поднимает Flask + сборку SPA)
```

### Линтинг / форматирование

```bash
make lint         # poetry run ruff check .
npm run lint      # eslint (frontend)
```

### Сборка

```bash
npm run build     # tsc -b && vite build (frontend)
```

## Структура проекта

```text
calendar_app/          # бэкенд Flask
  routes/              # HTML-маршруты гостя и владельца
  services/            # слоты и бронирования (бизнес-логика)
tests/                 # pytest (in-memory SQLite)
frontend/              # SPA React + Vite
  e2e/                 # Playwright-тесты (интеграционные)
typespec/              # API-контракт (источник истины)
openapi/openapi.yaml   # сгенерированная спецификация
docs/                  # доменная модель, контракт, сценарии
```

## Конвенции

- Conventional Commits (проверяется commitlint в CI и репозиторием):
  - формат: `<type>(<scope>): <описание>` — без заглавных букв в subject,
    максимум 100 символов;
  - типы: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`,
    `style`, `perf`, `revert`;
  - scope (по желанию): `backend`, `frontend`, `api`, `e2e`, `ci`, `docs`,
    `deps`, `release`, `admin`, `guest`;
  - примеры: `feat(frontend): add slot conflict message`,
    `fix(api): validate email length`, `test(e2e): cover guest booking flow`,
    `ci: add playwright job`;
  - один коммит = одно логическое изменение; тело коммита — при необходимости;
  - для агента правило обязательно: каждый коммит должен быть conventional.
- Правила выпуска: версия управляется release-please (бамп по conventional
  коммитам в `main`); release-тип — `python`, синхронно обновляется версия
  `frontend/package.json`.

## Важные замечания

- В контейнере приложение запускается через Gunicorn и слушает `0.0.0.0:$PORT`
  (переменная окружения `PORT`, по умолчанию 5000). При изменении запуска
  проверять, что `PORT` по-прежнему учитывается.
- `.github/workflows/hexlet-check.yml` и `.github/workflows/README.md` —
  служебные файлы Hexlet: их **нельзя редактировать, удалять или переименовывать**.
- Перед коммитом запускать `make test`, `make lint`, `npm run lint`,
  `npm run build` и (если менялся фронтенд) `npm run e2e`.
- Секреты и ключи не должны попадать в git. `e2e.sqlite` и артефакты
  Playwright (`test-results/`, `playwright-report/`) — в `.gitignore`.
