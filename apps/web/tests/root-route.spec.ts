import { expect, test } from "@playwright/test";

test("root route opens the studio directly", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(page.getByRole("heading", { name: "Theatrical Voice Studio" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vesper Glass" })).toBeVisible();
  await expect(page.getByRole("status", { name: "Voice rights status" })).toContainText(
    "Approved for generation",
  );
  await expect(page.getByRole("textbox", { name: "Generation text" })).toBeVisible();
  await expect(page.getByRole("group", { name: "Tone preset" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Generate voice" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Record turn" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Upload audio" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Spoken turns" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Recent attempts" })).toBeVisible();

  await expect(page.getByRole("button", { name: /retry/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /transcribe/i })).toHaveCount(0);
  await expect(page.getByLabel(/live conversation/i)).toHaveCount(0);
  await expect(page.getByRole("button", { name: /playback/i })).toHaveCount(0);
});
