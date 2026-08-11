import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { ApiError, createBooking, getEventType } from "../api";
import type { EventType } from "../types";
import { useAsync } from "../hooks/useAsync";
import { Alert } from "../components/Alert";
import { Spinner } from "../components/Spinner";

function formatSlotLabel(iso: string): string {
  return new Date(iso).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function BookingForm() {
  const { id } = useParams();
  const eventTypeId = Number(id);
  const [params] = useSearchParams();
  const start = params.get("start");
  const navigate = useNavigate();

  const eventType = useAsync<EventType>(() => getEventType(eventTypeId), [eventTypeId]);

  const [guestName, setGuestName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!start) {
    return <Alert variant="warning">Выберите свободный слот в календаре.</Alert>;
  }
  const startsAt = start;
  if (eventType.loading) return <Spinner />;
  if (eventType.error) return <Alert variant="danger">{eventType.error}</Alert>;
  if (!eventType.data) return null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const next: Record<string, string> = {};
    if (!guestName.trim()) next.guestName = "Укажите имя.";
    if (email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) next.email = "Некорректный email.";
    setFieldErrors(next);
    if (Object.keys(next).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      const booking = await createBooking({
        eventTypeId,
        startsAt,
        guestName: guestName.trim(),
        phone: phone.trim() || undefined,
        email: email.trim() || undefined,
      });
      navigate(`/bookings/${booking.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setSubmitError("Этот слот уже занят. Выберите другой слот.");
      } else {
        setSubmitError(err instanceof Error ? err.message : "Не удалось создать бронирование.");
      }
      setSubmitting(false);
    }
  }

  return (
    <>
      <h1 className="mb-2">Бронирование: {eventType.data.name}</h1>
      <p className="mb-4">
        Слот: <strong>{formatSlotLabel(startsAt)}</strong>
      </p>
      {submitError && <Alert variant="danger">{submitError}</Alert>}
      <form className="col-md-6" onSubmit={handleSubmit} noValidate>
        <div className="mb-3">
          <label className="form-label" htmlFor="guestName">
            Имя
          </label>
          <input
            id="guestName"
            className={`form-control${fieldErrors.guestName ? " is-invalid" : ""}`}
            value={guestName}
            onChange={(e) => setGuestName(e.target.value)}
          />
          {fieldErrors.guestName && <div className="invalid-feedback">{fieldErrors.guestName}</div>}
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="phone">
            Телефон
          </label>
          <input id="phone" className="form-control" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <div className="mb-3">
          <label className="form-label" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            className={`form-control${fieldErrors.email ? " is-invalid" : ""}`}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {fieldErrors.email && <div className="invalid-feedback">{fieldErrors.email}</div>}
        </div>
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          Забронировать
        </button>
        <Link className="btn btn-link" to={`/event-types/${eventTypeId}`}>
          Назад
        </Link>
      </form>
    </>
  );
}
