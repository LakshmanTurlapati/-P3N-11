import { expect, test } from "@playwright/test";

const BLOCKED_RIGHTS_MESSAGE =
  "Generation blocked: this voice profile is missing approved rights metadata.";

test("studio generation accepts text and a tone preset then surfaces a queued job", async ({
  page,
}) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Theatrical Voice Studio" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vesper Glass" })).toBeVisible();
  await expect(page.getByRole("status", { name: "Voice rights status" })).toContainText(
    "Approved for generation",
  );

  const generationText = page.getByRole("textbox", { name: "Generation text" });
  const toneGroup = page.getByRole("group", { name: "Tone preset" });
  const generateButton = page.getByRole("button", { name: "Generate voice" });
  const generationStatus = page.getByRole("status", { name: "Generation status" });
  const generationCard = page.getByRole("article", { name: "Generation job" });

  await expect(generationText).toBeVisible();
  await expect(toneGroup.getByRole("button", { name: "Measured" })).toBeVisible();
  await expect(toneGroup.getByRole("button", { name: "Cutting" })).toBeVisible();
  await expect(toneGroup.getByRole("button", { name: "Grandiose" })).toBeVisible();

  await generationText.fill("Deliver one measured, theatrical line.");
  await toneGroup.getByRole("button", { name: "Measured" }).click();

  const generationResponse = page.waitForResponse(
    (response) => response.url().endsWith("/generate") && response.request().method() === "POST",
  );

  await generateButton.click();

  const response = await generationResponse;
  expect(response.status()).toBe(200);

  const payload = (await response.json()) as {
    job_id: unknown;
    status: unknown;
    text: unknown;
    tone_preset: unknown;
  };

  expect(payload.job_id).toEqual(expect.any(String));
  expect(payload.status === "queued" || payload.status === "running").toBe(true);
  expect(payload.text).toBe("Deliver one measured, theatrical line.");
  expect(payload.tone_preset).toBe("measured");

  await expect(generationStatus).toContainText(/Queued|Running/);
  await expect(generationCard).toBeVisible();
  await expect(generationCard).toContainText("prototype baseline");
  await expect(generationCard).toContainText("Vesper Glass");
  await expect(generationCard).toContainText("Deliver one measured, theatrical line.");
  await expect(generationCard).toContainText("Measured");

  await expect(page.getByRole("button", { name: /retry/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /playback/i })).toHaveCount(0);
  await expect(page.getByLabel(/mic/i)).toHaveCount(0);
  await expect(page.getByLabel(/upload/i)).toHaveCount(0);
  await expect(page.getByLabel(/live conversation/i)).toHaveCount(0);
});

test("blocked voices still surface the exact rights message", async ({ page }) => {
  await page.route("**/generate", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }

    await route.fulfill({
      status: 403,
      contentType: "application/json",
      body: JSON.stringify({ detail: BLOCKED_RIGHTS_MESSAGE }),
    });
  });

  await page.goto("/");

  await page.getByRole("textbox", { name: "Generation text" }).fill("Blocked test line.");
  await page.getByRole("button", { name: "Cutting" }).click();
  await page.getByRole("button", { name: "Generate voice" }).click();

  await expect(page.getByRole("alert")).toContainText(BLOCKED_RIGHTS_MESSAGE);
});
