import { Link, useParams } from "react-router-dom";
import { getEventType, listSlots } from "../api";
import type { EventType, Slot } from "../types";
import { useAsync } from "../hooks/useAsync";
import { Alert } from "../components/Alert";
import { Spinner } from "../components/Spinner";

interface SlotDay {
  day: Date;
  slots: Slot[];
}

function groupByDay(slots: Slot[]): SlotDay[] {
  const map = new Map<string, SlotDay>();
  for (const slot of slots) {
    const start = new Date(slot.start);
    const key = start.toDateString();
    const existing = map.get(key);
    if (!existing) {
      map.set(key, { day: start, slots: [slot] });
    } else {
      existing.slots.push(slot);
    }
  }
  return [...map.values()].sort((a, b) => a.day.getTime() - b.day.getTime());
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}

function formatDay(day: Date): string {
  return day.toLocaleDateString("ru-RU", { weekday: "short", day: "numeric", month: "long" });
}

export function Calendar() {
  const { id } = useParams();
  const eventTypeId = Number(id);
  const eventType = useAsync<EventType>(() => getEventType(eventTypeId), [eventTypeId]);
  const slots = useAsync<Slot[]>(() => listSlots(eventTypeId), [eventTypeId]);

  if (eventType.loading || slots.loading) return <Spinner />;
  if (eventType.error) return <Alert variant="danger">{eventType.error}</Alert>;
  if (!eventType.data) return null;

  const days = groupByDay(slots.data ?? []);

  return (
    <>
      <h1 className="mb-1">{eventType.data.name}</h1>
      <p className="mb-2">{eventType.data.description}</p>
      <p className="text-muted mb-4">Длительность: {eventType.data.durationMinutes} мин.</p>
      {slots.error && <Alert variant="danger">{slots.error}</Alert>}
      {days.length === 0 && <Alert variant="info">Свободных слотов нет.</Alert>}
      {days.map(({ day, slots: daySlots }) => (
        <div className="mb-4" key={day.toISOString()}>
          <h2 className="h5">{formatDay(day)}</h2>
          <div className="d-flex flex-wrap gap-2">
            {daySlots.map((slot) => (
              <Link
                className="btn btn-outline-primary"
                key={slot.start}
                to={`/event-types/${eventTypeId}/book?start=${encodeURIComponent(slot.start)}`}
              >
                {formatTime(slot.start)}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </>
  );
}
