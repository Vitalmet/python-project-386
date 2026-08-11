import type {
  ApiErrorPayload,
  Booking,
  BookingCreate,
  EventType,
  EventTypeCreate,
  Slot,
  UpcomingMeetings,
} from "./types";
import { API_BASE_URL } from "./config";

export class ApiError extends Error {
  status: number;
  code: string;
  details?: string[];

  constructor(status: number, code: string, message: string, details?: string[]) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    let payload: Partial<ApiErrorPayload> = {};
    try {
      payload = (await response.json()) as Partial<ApiErrorPayload>;
    } catch {
      // тело ответа не JSON — используем заглушку
    }
    throw new ApiError(
      response.status,
      payload.code ?? "UNKNOWN_ERROR",
      payload.message ?? `Ошибка запроса (${response.status}).`,
      payload.details,
    );
  }
  return response.json() as Promise<T>;
}

function jsonRequest(body: unknown, method: string): RequestInit {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

export function listEventTypes(): Promise<EventType[]> {
  return request("/event-types");
}

export function getEventType(id: number): Promise<EventType> {
  return request(`/event-types/${id}`);
}

export function listSlots(id: number): Promise<Slot[]> {
  return request(`/event-types/${id}/slots`);
}

export function createBooking(payload: BookingCreate): Promise<Booking> {
  return request("/bookings", jsonRequest(payload, "POST"));
}

export function getBooking(id: number): Promise<Booking> {
  return request(`/bookings/${id}`);
}

export const adminApi = {
  listEventTypes(): Promise<EventType[]> {
    return request("/admin/event-types");
  },
  createEventType(payload: EventTypeCreate): Promise<EventType> {
    return request("/admin/event-types", jsonRequest(payload, "POST"));
  },
  upcomingBookings(): Promise<UpcomingMeetings> {
    return request("/admin/bookings/upcoming");
  },
};
