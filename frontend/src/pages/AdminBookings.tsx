import { adminApi } from "../api";
import type { Booking, EventType } from "../types";
import { useAsync } from "../hooks/useAsync";
import { Alert } from "../components/Alert";
import { Spinner } from "../components/Spinner";

interface UpcomingData {
  bookings: Booking[];
  typeNames: Map<number, string>;
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function AdminBookings() {
  const { data, error, loading } = useAsync<UpcomingData>(async () => {
    const [meetings, eventTypes] = await Promise.all([adminApi.upcomingBookings(), adminApi.listEventTypes()]);
    const typeNames = new Map(eventTypes.map((type: EventType) => [type.id, type.name]));
    return { bookings: meetings.bookings, typeNames };
  }, []);

  if (loading) return <Spinner />;
  if (error) return <Alert variant="danger">{error}</Alert>;

  const bookings = data?.bookings ?? [];

  return (
    <>
      <h1 className="mb-4">Предстоящие встречи</h1>
      {bookings.length === 0 && <Alert variant="info">Предстоящих встреч нет.</Alert>}
      {bookings.length > 0 && (
        <table className="table table-striped table-hover">
          <thead>
            <tr>
              <th>Когда</th>
              <th>Тип события</th>
              <th>Гость</th>
              <th>Контакты</th>
            </tr>
          </thead>
          <tbody>
            {bookings.map((booking) => (
              <tr key={booking.id}>
                <td>{formatDateTime(booking.startsAt)}</td>
                <td>{data?.typeNames.get(booking.eventTypeId) ?? `#${booking.eventTypeId}`}</td>
                <td>{booking.guestName}</td>
                <td>
                  {booking.phone && <span>{booking.phone} </span>}
                  {booking.email && <span>{booking.email}</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
