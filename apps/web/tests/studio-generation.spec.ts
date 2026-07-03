import { expect, type Page, test } from "@playwright/test";

const LIVE_TEST_TIMEOUT_MS = 240_000;
const POLL_INTERVALS_MS = [500, 1_000, 2_000];

const BLOCKED_RIGHTS_MESSAGE =
  "Generation blocked: this voice profile is missing approved rights metadata.";

const VOICE_ID = "vesper-glass";
const MEASURED_TEXT = "Deliver one measured, theatrical line.";
const CUTTING_TEXT = "Deliver one cutting line. playwright-fail-once";
const MUTATED_RETRY_TEXT = "Mutated text that should not be retried.";

type GenerationTonePreset = "measured" | "cutting" | "grandiose";
type GenerationJobStatus = "queued" | "running" | "succeeded" | "failed";

type GenerationJobRecord = {
  job_id: string;
  retry_of_job_id: string | null;
  status: GenerationJobStatus;
  voice_id: string;
  text: string;
  tone_preset: GenerationTonePreset;
  playback_url: string | null;
  audio_duration_ms: number | null;
  attempt: {
    status: GenerationJobStatus;
    provider_name: string | null;
    mime_type: string | null;
    error_message: string | null;
    audio_duration_ms: number | null;
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
};

test.describe.configure({ timeout: LIVE_TEST_TIMEOUT_MS });

const tonePresetLabels: Record<GenerationTonePreset, string> = {
  measured: "Measured",
  cutting: "Cutting",
  grandiose: "Grandiose",
};

function audioUrlMatcher(jobId: string) {
  return new RegExp(`/generations/${jobId}/audio$`);
}

async function submitLiveGeneration(
  page: Page,
  text: string,
  tonePreset: GenerationTonePreset,
) {
  const generateResponsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().endsWith("/generate") &&
      response.status() === 200,
  );

  await page.getByRole("button", { name: "Generate voice" }).click();

  const generateResponse = await generateResponsePromise;
  const generateRequest = generateResponse.request();
  const requestBody = generateRequest.postDataJSON() as {
    voice_id: string;
    text: string;
    tone_preset: GenerationTonePreset;
  };

  expect(generateResponse.status()).toBe(200);
  expect(requestBody).toEqual({
    voice_id: VOICE_ID,
    text,
    tone_preset: tonePreset,
  });

  const jobRecord = (await generateResponse.json()) as GenerationJobRecord;
  expect(jobRecord).toMatchObject({
    job_id: expect.any(String),
    retry_of_job_id: null,
    status: "queued",
    voice_id: VOICE_ID,
    text,
    tone_preset: tonePreset,
    playback_url: null,
    audio_duration_ms: null,
  });

  return jobRecord;
}

async function waitForGenerationRecord(
  page: Page,
  jobId: string,
  expectedStatus: GenerationJobStatus,
) {
  const generationUrl = new URL(`/generations/${jobId}`, page.url()).toString();
  let latestRecord: GenerationJobRecord | null = null;

  await expect
    .poll(
      async () => {
        const response = await page.request.get(generationUrl);
        expect(response.ok()).toBeTruthy();

        latestRecord = (await response.json()) as GenerationJobRecord;
        return latestRecord.status;
      },
      {
        timeout: LIVE_TEST_TIMEOUT_MS,
        intervals: POLL_INTERVALS_MS,
      },
    )
    .toBe(expectedStatus);

  if (!latestRecord) {
    throw new Error(`Generation ${jobId} did not return a record.`);
  }

  return latestRecord;
}

async function waitForLiveGeneration(
  page: Page,
  params: {
    jobId: string;
    text: string;
    tonePreset: GenerationTonePreset;
  },
) {
  const currentClip = page.getByRole("article", { name: "Current clip" });
  const currentClipAudio = currentClip.getByLabel("Current clip playback");

  const jobRecord = await waitForGenerationRecord(page, params.jobId, "succeeded");

  expect(jobRecord).toMatchObject({
    job_id: params.jobId,
    status: "succeeded",
    text: params.text,
    tone_preset: params.tonePreset,
    playback_url: `/generations/${params.jobId}/audio`,
  });

  await expect(page.getByRole("status", { name: "Generation status" })).toContainText(
    "Succeeded",
  );
  await expect(currentClip).toContainText(params.text);
  await expect(currentClip).toContainText(tonePresetLabels[params.tonePreset]);
  await expect(currentClip).not.toContainText("Prototype baseline stub");
  await expect(currentClipAudio).toHaveAttribute(
    "src",
    audioUrlMatcher(params.jobId),
  );

  return jobRecord;
}

test("studio generation surfaces a playable clip through the live backend", async ({
  page,
}) => {
  await page.goto("/");

  const currentClip = page.getByRole("article", { name: "Current clip" });
  const recentAttempts = page.getByRole("list", { name: "Recent attempts" });
  const generationStatus = page.getByRole("status", { name: "Generation status" });

  await expect(currentClip).toContainText("No playable clip yet.");
  await expect(recentAttempts).toContainText("No attempts yet.");

  await page.getByRole("textbox", { name: "Generation text" }).fill(MEASURED_TEXT);
  await page.getByRole("button", { name: "Measured" }).click();

  const queuedJob = await submitLiveGeneration(page, MEASURED_TEXT, "measured");
  await waitForLiveGeneration(page, {
    jobId: queuedJob.job_id,
    text: MEASURED_TEXT,
    tonePreset: "measured",
  });

  await expect(generationStatus).toContainText("Succeeded");
  await expect(currentClip).toContainText(queuedJob.job_id);
  await expect(currentClip).toContainText(MEASURED_TEXT);
  await expect(currentClip).toContainText("Measured");
  await expect(recentAttempts.getByRole("listitem")).toHaveCount(1);
  await expect(recentAttempts).toContainText(queuedJob.job_id);
  await expect(recentAttempts).toContainText("Succeeded");
  await expect(recentAttempts).not.toContainText("Prototype baseline stub");
});
