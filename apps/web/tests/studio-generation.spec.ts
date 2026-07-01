import { expect, test } from "@playwright/test";

test("studio generation posts the bundled voice and renders the structured metadata card", async ({
  page,
}) => {
  const requests: Array<Record<string, unknown>> = [];

  await page.route("**/generate", async (route) => {
    const body = route.request().postDataJSON() as Record<string, unknown>;
    requests.push(body);

    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        provider_type: "metadata-only-stub",
        voice_id: "vesper-glass",
        rights_check: {
          status: "approved",
          approved_for_generation: true,
          message: "Rights gate approved the bundled voice profile.",
        },
        result_metadata: {
          status: "metadata-only",
          summary: "Metadata-only stub generation completed without audio playback.",
          artifact_label: "Structured studio result card",
          provider_note:
            "Phase 1 keeps the stub provider inline in the API control plane.",
        },
        provider_trace: [
          {
            stage: "rights-gate",
            provider: "server-registry",
            detail: "Bundled Vesper Glass profile passed the approval check.",
          },
          {
            stage: "provider-boundary",
            provider: "metadata-only-stub",
            detail: "Speech-worker contracts stay swappable behind the metadata stub.",
          },
          {
            stage: "result-assembly",
            provider: "api-control-plane",
            detail: "Returned structured metadata only with no audio payload.",
          },
        ],
        timing: {
          started_at: "2026-07-01T00:00:00.000Z",
          ended_at: "2026-07-01T00:00:00.018Z",
          duration_ms: 18,
        },
      }),
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Generate stub reading" }).click();

  await expect(
    page.getByRole("heading", { name: "Generation result" }),
  ).toBeVisible();
  await expect(page.getByText("metadata-only-stub")).toBeVisible();
  await expect(page.getByText("vesper-glass")).toBeVisible();
  await expect(page.getByText("approved")).toBeVisible();
  await expect(page.getByText("Structured studio result card")).toBeVisible();
  await expect(page.getByText("rights-gate")).toBeVisible();
  await expect(page.getByText("18 ms")).toBeVisible();

  expect(requests).toHaveLength(1);
  expect(requests[0]).toEqual({ voice_id: "vesper-glass" });
});
