import { expect, test } from "@playwright/test";

test("studio generation posts the bundled voice and renders the structured metadata card", async ({
  page,
}) => {
  await page.goto("/");
  const generationResponse = page.waitForResponse(
    (response) => response.url().endsWith("/generate") && response.status() === 200,
  );

  await page.getByRole("button", { name: "Generate stub reading" }).click();
  await generationResponse;

  const generationCard = page.getByRole("article", { name: "Generation result" });

  await expect(generationCard).toBeVisible();
  await expect(generationCard).toContainText("metadata-only-stub");
  await expect(generationCard).toContainText("vesper-glass");
  await expect(generationCard).toContainText("approved");
  await expect(generationCard).toContainText("Structured studio result card");
  await expect(generationCard).toContainText("rights-gate");
  await expect(generationCard).toContainText("18 ms");
});
