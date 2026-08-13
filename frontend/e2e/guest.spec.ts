import { expect, test } from "@playwright/test";
import { createBooking, createEventType, listSlots, unique } from "./helpers";

const SLOT_LINK = /^(?:[01]\d|2[0-3]):[0-5]\d$/;

test.describe("Гость", () => {
  test("S1. Главная показывает список типов событий", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Виды брони" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Выбрать слот" }).first()).toBeVisible();
    await expect(page.getByText("Консультация", { exact: true })).toBeVisible();
  });

  test("S2. Календарь показывает свободные слоты", async ({ page, request }) => {
    const eventType = await createEventType(request, unique("Тип"), "Описание", 30);

    await page.goto(`/event-types/${eventType.id}`);

    await expect(page.getByRole("heading", { name: eventType.name })).toBeVisible();
    await expect(page.getByRole("link", { name: SLOT_LINK }).first()).toBeVisible();
  });

  test("S3. Гость создаёт бронирование", async ({ page, request }) => {
    const eventType = await createEventType(request, unique("Тип"), "Описание", 30);
    const slots = await listSlots(request, eventType.id);
    expect(slots.length).toBeGreaterThan(0);
    const start = encodeURIComponent(slots[0].start);

    await page.goto(`/event-types/${eventType.id}/book?start=${start}`);
    await expect(page.getByRole("heading", { name: /Бронирование/ })).toBeVisible();

    await page.getByLabel("Имя").fill("Иван");
    await page.getByLabel("Телефон").fill("+7 900 000-00-00");
    await page.getByLabel("Email").fill("ivan@example.com");
    await page.getByRole("button", { name: "Забронировать" }).click();

    await expect(page.getByRole("heading", { name: "Бронирование подтверждено" })).toBeVisible();
    await expect(page.getByText("Иван")).toBeVisible();
  });

  test("S4. Страница подтверждения отображает данные брони", async ({ page, request }) => {
    const eventType = await createEventType(request, unique("Тип"), "Описание", 30);
    const slots = await listSlots(request, eventType.id);
    expect(slots.length).toBeGreaterThan(0);
    const booking = await createBooking(request, eventType.id, slots[0].start, "Иван");

    await page.goto(`/bookings/${booking.id}`);

    await expect(page.getByRole("heading", { name: "Бронирование подтверждено" })).toBeVisible();
    await expect(page.getByText("Иван")).toBeVisible();
    await expect(page.getByText(new RegExp(`Номер брони: ${booking.id}`))).toBeVisible();
  });

  test("S5. Слот уже занят — ошибка", async ({ page, request }) => {
    const eventType = await createEventType(request, unique("Тип"), "Описание", 30);
    const slots = await listSlots(request, eventType.id);
    expect(slots.length).toBeGreaterThan(0);
    const target = slots[0];
    await createBooking(request, eventType.id, target.start, "Анна");

    await page.goto(`/event-types/${eventType.id}/book?start=${encodeURIComponent(target.start)}`);
    await page.getByLabel("Имя").fill("Иван");
    await page.getByRole("button", { name: "Забронировать" }).click();

    await expect(page.getByText("Этот слот уже занят. Выберите другой слот.")).toBeVisible();
  });

  test("S6. Валидация: пустое имя и некорректный email", async ({ page, request }) => {
    const eventType = await createEventType(request, unique("Тип"), "Описание", 30);
    const slots = await listSlots(request, eventType.id);
    expect(slots.length).toBeGreaterThan(0);
    const url = `/event-types/${eventType.id}/book?start=${encodeURIComponent(slots[0].start)}`;

    await page.goto(url);
    await page.getByRole("button", { name: "Забронировать" }).click();
    await expect(page.getByText("Укажите имя.")).toBeVisible();

    await page.getByLabel("Имя").fill("Иван");
    await page.getByLabel("Email").fill("не-email");
    await page.getByRole("button", { name: "Забронировать" }).click();
    await expect(page.getByText("Некорректный email.")).toBeVisible();

    await expect(page.getByRole("heading", { name: /Бронирование подтверждено/ })).not.toBeVisible();
  });
});