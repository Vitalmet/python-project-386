import { Link } from "react-router-dom";
import { listEventTypes } from "../api";
import type { EventType } from "../types";
import { useAsync } from "../hooks/useAsync";
import { Alert } from "../components/Alert";
import { Spinner } from "../components/Spinner";

export function Home() {
  const { data: eventTypes, error, loading } = useAsync<EventType[]>(listEventTypes, []);

  if (loading) return <Spinner />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!eventTypes || eventTypes.length === 0) {
    return <Alert variant="info">Типы событий пока не добавлены.</Alert>;
  }

  return (
    <>
      <h1 className="mb-4">Виды брони</h1>
      <div className="row row-cols-1 row-cols-md-2 g-4">
        {eventTypes.map((eventType) => (
          <div className="col" key={eventType.id}>
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">{eventType.name}</h5>
                <p className="card-text">{eventType.description}</p>
                <p className="text-muted mb-3">Длительность: {eventType.durationMinutes} мин.</p>
                <Link className="btn btn-primary" to={`/event-types/${eventType.id}`}>
                  Выбрать слот
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
