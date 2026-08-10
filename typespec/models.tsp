import "@typespec/http";

using TypeSpec.Http;

/** Идентификатор сущности. */
scalar EntityId extends int32;

/**
 * Тип события (вид брони), который владелец предлагает гостям.
 */
@doc("Тип события")
model EventType {
  /** Числовой идентификатор типа события. */
  id: EntityId;

  /** Название типа события, уникальное в системе. */
  @minLength(1)
  @maxLength(100)
  name: string;

  /** Описание типа события. */
  @minLength(1)
  description: string;

  /** Длительность события в минутах. */
  @minValue(1)
  durationMinutes: int32;
}

/** Данные для создания типа события владельцем. */
model EventTypeCreate {
  /** Название типа события. */
  @minLength(1)
  @maxLength(100)
  name: string;

  /** Описание типа события. */
  @minLength(1)
  description: string;

  /** Длительность события в минутах. */
  @minValue(1)
  durationMinutes: int32;
}

/**
 * Свободный слот бронирования в окне 14 дней.
 * Слот вычисляется сервисом доступности и не хранится в БД.
 */
model Slot {
  /** Начало слота (ISO 8601). */
  start: utcDateTime;

  /** Конец слота: start + durationMinutes типа события. */
  end: utcDateTime;

  /** Свободен ли слот для бронирования. */
  available: boolean;
}

/** Бронирование гостя на слот типа события. */
model Booking {
  /** Идентификатор бронирования. */
  id: EntityId;

  /** Тип события, на который записан гость. */
  eventTypeId: EntityId;

  /** Имя гостя. */
  @minLength(1)
  guestName: string;

  /** Телефон гостя (опционально). */
  phone?: string;

  /** Email гостя (опционально). */
  email?: string;

  /** Начало бронирования (ISO 8601). */
  startsAt: utcDateTime;

  /** Дата создания бронирования. */
  createdAt: utcDateTime;
}

/** Данные для создания бронирования гостем. */
model BookingCreate {
  /** Тип события, на который гость хочет записаться. */
  eventTypeId: EntityId;

  /** Начало выбранного слота (ISO 8601). */
  startsAt: utcDateTime;

  /** Имя гостя. */
  @minLength(1)
  guestName: string;

  /** Телефон гостя (опционально). */
  phone?: string;

  /** Email гостя (опционально). */
  email?: string;
}

/**
 * Список предстоящих встреч для владельца.
 * Содержит бронирования всех типов событий, отсортированные по времени.
 */
model UpcomingMeetings {
  /** Бронирования всех типов событий. */
  bookings: Booking[];
}

/** Обёртка успешного создания ресурса: статус 201 Created. */
model Created<T> {
  @statusCode statusCode: 201;
  @body body: T;
}

/** Ресурс не найден. */
@error
model NotFoundError {
  @statusCode statusCode: 404;
  code: "NOT_FOUND";
  message: string;
}

/** Слот занят: на это время уже есть бронирование (любого типа события). */
@error
model ConflictError {
  @statusCode statusCode: 409;
  code: "SLOT_BUSY";
  message: string;
}

/** Некорректные входные данные. */
@error
model ValidationError {
  @statusCode statusCode: 400;
  code: "VALIDATION_ERROR";
  message: string;
  details?: string[];
}
