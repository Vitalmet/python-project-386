import type { APIRequestContext } from "@playwright/test";

export const BACKEND_URL = "http://localhost:5000";

export interface EventType {
  id: number;
  name: string;
  description: string;
  durationMinutes: number;
}

export interface Slot {
  start: string;
  end: string;
  available: boolean;
}

export function unique(label: string): string {
  return `${label}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

export async function listEventTypes(request: APIRequestContext): Promise<EventType[]> {
  const response = await request.get(`${BACKEND_URL}/event-types`);
  if (!response.ok()) throw new Error(`listEventTypes: ${response.status()} ${await response.text()}`);
  return (await response.json()) as EventType[];
}

export async function listSlots(request: APIRequestContext, eventTypeId: number): Promise<Slot[]> {
  const response = await request.get(`${BACKEND_URL}/event-types/${eventTypeId}/slots`);
  if (!response.ok()) throw new Error(`listSlots: ${response.status()} ${await response.text()}`);
  return (await response.json()) as Slot[];
}

export async function createEventType(
  request: APIRequestContext,
  name: string,
  description: string,
  durationMinutes = 30,
): Promise<EventType> {
  const response = await request.post(`${BACKEND_URL}/admin/event-types`, {
    data: { name, description, durationMinutes },
  });
  if (!response.ok()) throw new Error(`createEventType: ${response.status()} ${await response.text()}`);
  return (await response.json()) as EventType;
}

export async function createBooking(
  request: APIRequestContext,
  eventTypeId: number,
  startsAt: string,
  guestName: string,
): Promise<{ id: number }> {
  const response = await request.post(`${BACKEND_URL}/bookings`, {
    data: { eventTypeId, startsAt, guestName },
  });
  if (!response.ok()) throw new Error(`createBooking: ${response.status()} ${await response.text()}`);
  return (await response.json()) as { id: number };
}