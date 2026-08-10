import "@typespec/http";
import "./models.tsp";

using TypeSpec.Http;

namespace CallCalendar {

  /** Публичные операции гостя: виды брони и бронирование. */
  @route("/event-types")
  namespace EventTypes {
    @doc("Список типов событий для гостя: название, описание, длительность.")
    @get
    op list(): EventType[];

    @doc("Информация о конкретном типе события.")
    @route("/{eventTypeId}")
    @get
    op get(@path eventTypeId: EntityId): EventType | NotFoundError;

    @doc("Свободные слоты типа события в окне бронирования. По умолчанию окно — 14 дней начиная с текущей даты.")
    @route("/{eventTypeId}/slots")
    @get
    op listSlots(
      @path eventTypeId: EntityId,
      @query from?: utcDateTime,
      @query to?: utcDateTime,
    ): Slot[] | NotFoundError;
  }

  /** Бронирование слотов гостем. */
  @route("/bookings")
  namespace Bookings {
    @doc("Создание бронирования на выбранный свободный слот.")
    @post
    op create(
      @body body: BookingCreate,
    ): Created<Booking> | ConflictError | ValidationError;

    @doc("Подтверждение созданного бронирования.")
    @route("/{bookingId}")
    @get
    op get(@path bookingId: EntityId): Booking | NotFoundError;
  }

  /**
   * Админские операции владельца календаря.
   * Владелец — один предзаданный профиль, используется по умолчанию,
   * авторизация в системе отсутствует.
   */
  @route("/admin")
  namespace Admin {
    @route("/event-types")
    namespace EventTypes {
      @doc("Список типов событий для владельца.")
      @get
      op list(): EventType[];

      @doc("Создание типа события владельцем.")
      @post
      op create(@body body: EventTypeCreate): Created<EventType> | ValidationError;
    }

    @route("/bookings")
    namespace Bookings {
      @doc("Предстоящие встречи: единый список бронирований всех типов событий, отсортированный по времени начала, только будущие встречи.")
      @route("/upcoming")
      @get
      op listUpcoming(@query from?: utcDateTime): UpcomingMeetings;
    }
  }
}
