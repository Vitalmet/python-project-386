import { expect, test } from "@playwright/test";
import { createBooking, createEventType, listSlots, unique } from "./helpers";

test.describe("Владелец", () => {
  test("S7. Создание типа события", async ({ page }) => {
    const name = unique("Новый тип");

    await page.goto("/admin/event-types");
    await page.getByLabel("Название").fill(name);
    await page.getByLabel("Описание").fill(`Описание для ${name}`);
    await page.getByLabel("Длительность (минуты)").fill("45");
    await page.getByRole("button", { name: "Создать" }).click();

    await expect(page.getByRole("cell", { name, exact: true })).toBeVisible();
  });

  test("S8. Дубликат названия типа события", async ({ page }) => {
    await page.goto("/admin/event-types");
    await page.getByLabel("Название").fill("Консультация");
    await page.getByLabel("Описание").fill("Ещё одна консультация");
    await page.getByLabel("Длительность (минуты)").fill("30");
    await page.getByRole("button", { name: "Создать" }).click();

    await expect(page.getByText("Тип события с таким названием уже существует.")).toBeVisible();
  });

  test("S9. Предстоящие встречи", async ({ page, request }) => {
    const eventType = await createEventType(request, unique("Тип"), "Описание", 30);
    const slots = await listSlots(request, eventType.id);
    expect(slots.length).toBeGreaterThan(0);
    await createBooking(request, eventType.id, slots[0].start, "Марк");

    await page.goto("/admin/bookings");
    await expect(page.getByText("Марк", { exact: true })).toBeVisible();
  });
});