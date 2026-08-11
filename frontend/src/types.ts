export interface EventType {
  id: number;
  name: string;
  description: string;
  durationMinutes: number;
}

export interface EventTypeCreate {
  name: string;
  description: string;
  durationMinutes: number;
}

export interface Slot {
  start: string;
  end: string;
  available: boolean;
}

export interface Booking {
  id: number;
  eventTypeId: number;
  guestName: string;
  phone?: string | null;
  email?: string | null;
  startsAt: string;
  createdAt: string;
}

export interface BookingCreate {
  eventTypeId: number;
  startsAt: string;
  guestName: string;
  phone?: string;
  email?: string;
}

export interface UpcomingMeetings {
  bookings: Booking[];
}

export type ErrorCode = "NOT_FOUND" | "SLOT_BUSY" | "VALIDATION_ERROR";

export interface ApiErrorPayload {
  code: string;
  message: string;
  details?: string[];
}
