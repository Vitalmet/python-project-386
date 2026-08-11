import { Link, useParams } from "react-router-dom";
import { getBooking } from "../api";
import type { Booking } from "../types";
import { useAsync } from "../hooks/useAsync";
import { Alert } from "../components/Alert";
import { Spinner } from "../components/Spinner";

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function BookingSuccess() {
  const { id } = useParams();
  const bookingId = Number(id);
  const { data: booking, error, loading } = useAsync<Booking>(() => getBooking(bookingId), [bookingId]);

  if (loading) return <Spinner />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!booking) return null;

  return (
    <>
      <h1 className="mb-4">Бронирование подтверждено</h1>
      <div className="card" style={{ maxWidth: 480 }}>
        <div className="card-body">
          <p>
            <strong>Гость:</strong> {booking.guestName}
          </p>
          <p>
            <strong>Время:</strong> {formatDateTime(booking.startsAt)}
          </p>
          <p>
            <strong>Номер брони:</strong> {booking.id}
          </p>
          <Link className="btn btn-primary" to="/">
            К видам брони
          </Link>
        </div>
      </div>
    </>
  );
}
