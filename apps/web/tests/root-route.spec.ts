import { expect, test } from "@playwright/test";

test("root route opens the studio directly", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(
    page.getByRole("heading", { name: "Theatrical Voice Studio" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Vesper Glass" }),
  ).toBeVisible();
  await expect(page.getByRole("status")).toContainText("Approved for generation");
  await expect(page.getByRole("button", { name: "Generate stub reading" })).toBeVisible();

  await expect(page.getByRole("textbox")).toHaveCount(0);
  await expect(page.getByLabel(/tone preset/i)).toHaveCount(0);
  await expect(page.getByRole("button", { name: /retry/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /playback/i })).toHaveCount(0);
  await expect(page.getByLabel(/mic/i)).toHaveCount(0);
});
