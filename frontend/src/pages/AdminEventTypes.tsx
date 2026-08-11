import { useState } from "react";
import type { FormEvent } from "react";
import { adminApi, ApiError } from "../api";
import type { EventType } from "../types";
import { useAsync } from "../hooks/useAsync";
import { Alert } from "../components/Alert";
import { Spinner } from "../components/Spinner";

export function AdminEventTypes() {
  const { data: eventTypes, error, loading, reload } = useAsync<EventType[]>(adminApi.listEventTypes, []);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState("30");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    const next: Record<string, string> = {};
    if (!name.trim()) next.name = "Укажите название.";
    if (!description.trim()) next.description = "Укажите описание.";
    const durationNumber = Number(duration);
    if (!Number.isInteger(durationNumber) || durationNumber < 1) {
      next.duration = "Длительность должна быть целым числом больше 0.";
    }
    setFieldErrors(next);
    if (Object.keys(next).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      await adminApi.createEventType({
        name: name.trim(),
        description: description.trim(),
        durationMinutes: durationNumber,
      });
      setName("");
      setDescription("");
      setDuration("30");
      reload();
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setSubmitError(err.message);
      } else {
        setSubmitError(err instanceof Error ? err.message : "Не удалось создать тип события.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <Spinner />;

  return (
    <>
      <h1 className="mb-4">Типы событий</h1>
      {error && <Alert variant="danger">{error}</Alert>}
      {submitError && <Alert variant="danger">{submitError}</Alert>}

      <div className="card mb-4" style={{ maxWidth: 560 }}>
        <div className="card-body">
          <h2 className="h5 mb-3">Новый тип события</h2>
          <form onSubmit={handleCreate} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="et-name">
                Название
              </label>
              <input
                id="et-name"
                className={`form-control${fieldErrors.name ? " is-invalid" : ""}`}
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
              {fieldErrors.name && <div className="invalid-feedback">{fieldErrors.name}</div>}
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="et-description">
                Описание
              </label>
              <textarea
                id="et-description"
                className={`form-control${fieldErrors.description ? " is-invalid" : ""}`}
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              {fieldErrors.description && <div className="invalid-feedback">{fieldErrors.description}</div>}
            </div>
            <div className="mb-3">
              <label className="form-label" htmlFor="et-duration">
                Длительность (минуты)
              </label>
              <input
                id="et-duration"
                className={`form-control${fieldErrors.duration ? " is-invalid" : ""}`}
                type="number"
                min={1}
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
              {fieldErrors.duration && <div className="invalid-feedback">{fieldErrors.duration}</div>}
            </div>
            <button className="btn btn-primary" type="submit" disabled={submitting}>
              Создать
            </button>
          </form>
        </div>
      </div>

      {eventTypes && eventTypes.length === 0 && <Alert variant="info">Типы событий пока не добавлены.</Alert>}
      {eventTypes && eventTypes.length > 0 && (
        <table className="table table-striped table-hover">
          <thead>
            <tr>
              <th>Название</th>
              <th>Описание</th>
              <th>Длительность</th>
            </tr>
          </thead>
          <tbody>
            {eventTypes.map((eventType) => (
              <tr key={eventType.id}>
                <td>{eventType.name}</td>
                <td>{eventType.description}</td>
                <td>{eventType.durationMinutes} мин.</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
