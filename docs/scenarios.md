# Пользовательские сценарии для проверки

Зафиксированные сценарии — источник истины для интеграционных тестов.
Каждый сценарий покрыт E2E-тестом на Playwright (`frontend/e2e/`) и, где
отмечено, существующими pytest-тестами бэкенда.

Тестовое окружение: SPA-фронтенд (React) общается с бэкендом (Flask)
по контракту `openapi/openapi.yaml`. E2E поднимает Flask (отдельная БД
`e2e.sqlite` с демо-данными `flask seed`) и продакшн-сборку SPA.

## Гость

### S1. Список типов событий
Гость открывает главную страницу и видит карточки всех доступных типов
событий: название, описание, длительность.
- E2E: `guest.spec.ts`
- pytest: `test_guest.py::test_index_lists_event_types`, `test_api.py::test_api_list_event_types`

### S2. Календарь свободных слотов
Гость открывает тип события и видит свободные слоты на ближайшие 14 дней
(будни 09:00–18:00, шаг 30 минут).
- E2E: `guest.spec.ts`
- pytest: `test_slots.py`, `test_guest.py::test_calendar_shows_slots`

### S3. Создание бронирования (основной флоу)
Гость выбирает свободный слот, указывает имя (обязательно) и опционально
телефон/email, подтверждает бронирование.
- E2E: `guest.spec.ts`
- pytest: `test_guest.py::test_booking_flow`, `test_api.py::test_api_create_booking`

### S4. Подтверждение бронирования
После создания гость видит страницу подтверждения: имя, дата/время, номер брони.
- E2E: `guest.spec.ts`
- pytest: `test_guest.py::test_booking_flow`, `test_api.py::test_api_get_booking`

### S5. Слот уже занят
Слот, занятый бронированием (в т.ч. другого типа события), недоступен для
повторной брони: система показывает понятное сообщение об ошибке.
- E2E: `guest.spec.ts`
- pytest: `test_guest.py::test_duplicate_booking_conflict`, `test_api.py::test_api_create_booking_busy`, `test_bookings.py::test_same_slot_conflict_across_types`

### S6. Валидация формы брони
Пустое имя → ошибка «Укажите имя». Некорректный email → ошибка.
Бронирование не создаётся.
- E2E: `guest.spec.ts`
- pytest: `test_guest.py::test_booking_requires_guest_name`, `test_api.py::test_api_create_booking_validation`

## Владелец

### S7. Создание типа события
Владелец создаёт тип события через админку (название, описание, длительность).
Созданный тип появляется в списке типов.
- E2E: `admin.spec.ts`
- pytest: `test_admin.py::test_admin_creates_event_type`, `test_api.py::test_api_admin_create`

### S8. Дубликат названия типа события
Создание типа с уже существующим названием отклоняется с ошибкой.
- E2E: `admin.spec.ts`
- pytest: `test_admin.py::test_admin_rejects_duplicate_name`, `test_api.py::test_api_admin_create_duplicate`

### S9. Предстоящие встречи
Владелец видит единый список будущих встреч всех типов событий,
отсортированный по времени начала; прошедшие брони не показываются.
- E2E: `admin.spec.ts`
- pytest: `test_admin.py::test_upcoming_bookings_list_only_future`, `test_api.py::test_api_admin_upcoming`