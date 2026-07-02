import { expect, type Page, test } from "@playwright/test";

const BLOCKED_RIGHTS_MESSAGE =
  "Generation blocked: this voice profile is missing approved rights metadata.";

type GenerationTonePreset = "measured" | "cutting" | "grandiose";
type GenerationJobStatus = "queued" | "running" | "succeeded" | "failed";

type GenerationJobRecord = {
  provider_type: string | null;
  provider_name: string | null;
  job_id: string;
  retry_of_job_id: string | null;
  status: GenerationJobStatus;
  voice_id: string;
  text: string;
  tone_preset: GenerationTonePreset;
  rights_check: {
    status: "approved";
    approved_for_generation: boolean;
    message: string;
  };
  provider_trace: Array<{
    stage: string;
    provider: string;
    detail: string;
  }>;
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
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
  playback_url: string | null;
  audio_duration_ms: number | null;
};

type JobPlan = {
  responses: GenerationJobRecord[];
  audioBytes?: Buffer;
};

const VOICE_ID = "vesper-glass";
const STARTED_AT = "2026-07-02T18:00:00.000Z";
const ENDED_AT = "2026-07-02T18:00:00.314Z";
const AUDIO_BYTES = Buffer.from("RIFFphase2-audio");

function createJobRecord({
  jobId,
  status,
  text,
  tonePreset,
  providerName = null,
  providerType = null,
  retryOfJobId = null,
  playbackUrl = null,
  audioDurationMs = null,
  errorMessage = null,
}: {
  jobId: string;
  status: GenerationJobStatus;
  text: string;
  tonePreset: GenerationTonePreset;
  providerName?: string | null;
  providerType?: string | null;
  retryOfJobId?: string | null;
  playbackUrl?: string | null;
  audioDurationMs?: number | null;
  errorMessage?: string | null;
}): GenerationJobRecord {
  const attemptProviderName = status === "queued" ? null : providerName;
  const attemptErrorMessage = status === "failed" ? errorMessage ?? "Generation failed." : null;

  return {
    provider_type: providerType,
    provider_name: providerName,
    job_id: jobId,
    retry_of_job_id: retryOfJobId,
    status,
    voice_id: VOICE_ID,
    text,
    tone_preset: tonePreset,
    rights_check: {
      status: "approved",
      approved_for_generation: true,
      message: "Rights gate approved the bundled voice profile.",
    },
    provider_trace: [
      {
        stage: "rights-gate",
        provider: "server-registry",
        detail: "Bundled Vesper Glass profile passed the approval check.",
      },
      {
        stage: "job-queue",
        provider: "api-control-plane",
        detail: "Queued a generation job with the submitted text and tone preset.",
      },
      {
        stage: "provider-boundary",
        provider: "job-service",
        detail: "Speech-worker contracts stay swappable behind the job-backed generation route.",
      },
    ],
    timing: {
      started_at: STARTED_AT,
      ended_at: ENDED_AT,
      duration_ms: 314,
    },
    attempt: {
      status,
      provider_name: attemptProviderName,
      mime_type: status === "succeeded" ? "audio/wav" : null,
      error_message: attemptErrorMessage,
      audio_duration_ms: status === "succeeded" ? audioDurationMs ?? 1536 : null,
      started_at: STARTED_AT,
      ended_at: ENDED_AT,
      duration_ms: 314,
    },
    playback_url: playbackUrl,
    audio_duration_ms: audioDurationMs,
  };
}

async function installGenerationHarness(page: Page, jobPlans: JobPlan[]) {
  const generatedBodies: Array<{
    voice_id: string;
    text: string;
    tone_preset: GenerationTonePreset;
  }> = [];
  const jobPlansById = new Map<string, JobPlan>();
  const pollCounts = new Map<string, number>();
  let generateCallIndex = 0;

  await page.route("**/generate", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }

    const request = route.request().postDataJSON() as {
      voice_id: string;
      text: string;
      tone_preset: GenerationTonePreset;
    };
    const plan = jobPlans[generateCallIndex];

    if (!plan) {
      throw new Error("Unexpected generation request in test harness.");
    }

    generatedBodies.push(request);
    jobPlansById.set(plan.responses[0].job_id, plan);
    generateCallIndex += 1;

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(plan.responses[0]),
    });
  });

  await page.route("**/generations/**", async (route) => {
    const requestUrl = new URL(route.request().url());
    const pathParts = requestUrl.pathname.split("/").filter(Boolean);
    const jobId = pathParts[1];
    const plan = jobPlansById.get(jobId);

    if (!plan) {
      await route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Generation job not found." }),
      });
      return;
    }

    if (requestUrl.pathname.endsWith("/audio")) {
      await route.fulfill({
        status: 200,
        contentType: "audio/wav",
        body: plan.audioBytes ?? AUDIO_BYTES,
      });
      return;
    }

    const pollCount = pollCounts.get(jobId) ?? 0;
    const response = plan.responses[Math.min(pollCount, plan.responses.length - 1)];
    pollCounts.set(jobId, pollCount + 1);

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(response),
    });
  });

  return {
    generatedBodies,
  };
}

test("studio generation surfaces a playable clip, recent attempts, and retry from session state", async ({
  page,
}) => {
  const harness = await installGenerationHarness(page, [
    {
      responses: [
        createJobRecord({
          jobId: "job-playback-1",
          status: "queued",
          text: "Deliver one measured, theatrical line.",
          tonePreset: "measured",
        }),
        createJobRecord({
          jobId: "job-playback-1",
          status: "running",
          text: "Deliver one measured, theatrical line.",
          tonePreset: "measured",
        }),
        createJobRecord({
          jobId: "job-playback-1",
          status: "succeeded",
          text: "Deliver one measured, theatrical line.",
          tonePreset: "measured",
          providerName: "Prototype baseline stub",
          providerType: "prototype-baseline-stub",
          playbackUrl: "/generations/job-playback-1/audio",
          audioDurationMs: 1536,
        }),
      ],
      audioBytes: AUDIO_BYTES,
    },
  ]);

  await page.goto("/");

  const currentClip = page.getByRole("article", { name: "Current clip" });
  const recentAttempts = page.getByRole("list", { name: "Recent attempts" });
  const generationStatus = page.getByRole("status", { name: "Generation status" });

  await expect(currentClip).toContainText("No playable clip yet.");
  await expect(recentAttempts).toContainText("No attempts yet.");

  await page.getByRole("textbox", { name: "Generation text" }).fill(
    "Deliver one measured, theatrical line.",
  );
  await page.getByRole("button", { name: "Measured" }).click();

  await page.getByRole("button", { name: "Generate voice" }).click();

  await expect(generationStatus).toContainText("Queued");
  await expect(generationStatus).toContainText("Running");
  await expect(generationStatus).toContainText("Succeeded");

  await expect(currentClip).toContainText("Deliver one measured, theatrical line.");
  await expect(currentClip).toContainText("Measured");
  await expect(currentClip).toContainText("Prototype baseline stub");
  await expect(currentClip).toContainText("1536 ms");
  await expect(currentClip.getByLabel("Current clip playback")).toHaveAttribute(
    "src",
    /\/generations\/job-playback-1\/audio$/,
  );

  await expect(recentAttempts.getByRole("listitem")).toHaveCount(1);
  await expect(recentAttempts).toContainText("job-playback-1");
  await expect(recentAttempts).toContainText("Succeeded");
  await expect(recentAttempts).toContainText("Prototype baseline stub");
  await expect(recentAttempts).toContainText("314 ms");

  await page.reload();

  await expect(page.getByRole("article", { name: "Current clip" })).toContainText(
    "No playable clip yet.",
  );
  await expect(page.getByRole("list", { name: "Recent attempts" })).toContainText(
    "No attempts yet.",
  );

  expect(harness.generatedBodies).toEqual([
    {
      voice_id: VOICE_ID,
      text: "Deliver one measured, theatrical line.",
      tone_preset: "measured",
    },
  ]);
});

test("retry reuses the last voice, text, and tone after a failed attempt", async ({
  page,
}) => {
  const harness = await installGenerationHarness(page, [
    {
      responses: [
        createJobRecord({
          jobId: "job-failure-1",
          status: "queued",
          text: "Deliver one cutting line.",
          tonePreset: "cutting",
        }),
        createJobRecord({
          jobId: "job-failure-1",
          status: "running",
          text: "Deliver one cutting line.",
          tonePreset: "cutting",
        }),
        createJobRecord({
          jobId: "job-failure-1",
          status: "failed",
          text: "Deliver one cutting line.",
          tonePreset: "cutting",
          providerName: "Prototype baseline stub",
          providerType: "prototype-baseline-stub",
          errorMessage: "Generation failed after job polling.",
        }),
      ],
      audioBytes: AUDIO_BYTES,
    },
    {
      responses: [
        createJobRecord({
          jobId: "job-retry-2",
          status: "queued",
          text: "Deliver one cutting line.",
          tonePreset: "cutting",
          retryOfJobId: "job-failure-1",
        }),
        createJobRecord({
          jobId: "job-retry-2",
          status: "running",
          text: "Deliver one cutting line.",
          tonePreset: "cutting",
          retryOfJobId: "job-failure-1",
        }),
        createJobRecord({
          jobId: "job-retry-2",
          status: "succeeded",
          text: "Deliver one cutting line.",
          tonePreset: "cutting",
          providerName: "Prototype baseline stub",
          providerType: "prototype-baseline-stub",
          retryOfJobId: "job-failure-1",
          playbackUrl: "/generations/job-retry-2/audio",
          audioDurationMs: 1422,
        }),
      ],
      audioBytes: AUDIO_BYTES,
    },
  ]);

  await page.goto("/");

  const currentClip = page.getByRole("article", { name: "Current clip" });
  const recentAttempts = page.getByRole("list", { name: "Recent attempts" });
  const generationStatus = page.getByRole("status", { name: "Generation status" });

  await page.getByRole("textbox", { name: "Generation text" }).fill(
    "Deliver one cutting line.",
  );
  await page.getByRole("button", { name: "Cutting" }).click();

  await page.getByRole("button", { name: "Generate voice" }).click();

  await expect(generationStatus).toContainText("Queued");
  await expect(generationStatus).toContainText("Running");
  await expect(generationStatus).toContainText("Failed");
  await expect(page.locator('p[role="alert"]')).toContainText(
    "Generation failed after job polling.",
  );

  await expect(currentClip).toContainText("No playable clip yet.");
  await expect(recentAttempts.getByRole("listitem")).toHaveCount(1);
  await expect(recentAttempts).toContainText("job-failure-1");
  await expect(recentAttempts).toContainText("Failed");
  await expect(recentAttempts).toContainText("Prototype baseline stub");

  await page.getByRole("textbox", { name: "Generation text" }).fill(
    "Mutated text that should not be retried.",
  );
  await page.getByRole("button", { name: "Grandiose" }).click();

  const retryRequestPromise = page.waitForRequest((request) => {
    if (request.url().endsWith("/generate") && request.method() === "POST") {
      return request.postDataJSON().text === "Deliver one cutting line.";
    }

    return false;
  });

  await page.getByRole("button", { name: "Retry current generation" }).click();

  const retryRequest = await retryRequestPromise;
  expect(retryRequest.postDataJSON()).toEqual({
    voice_id: VOICE_ID,
    text: "Deliver one cutting line.",
    tone_preset: "cutting",
  });

  await expect(generationStatus).toContainText("Queued");
  await expect(generationStatus).toContainText("Running");
  await expect(generationStatus).toContainText("Succeeded");

  await expect(currentClip).toContainText("Deliver one cutting line.");
  await expect(currentClip).toContainText("Cutting");
  await expect(currentClip).toContainText("Prototype baseline stub");
  await expect(currentClip.getByLabel("Current clip playback")).toHaveAttribute(
    "src",
    /\/generations\/job-retry-2\/audio$/,
  );

  await expect(recentAttempts.getByRole("listitem")).toHaveCount(2);
  await expect(recentAttempts).toContainText("job-failure-1");
  await expect(recentAttempts).toContainText("Failed");
  await expect(recentAttempts).toContainText("job-retry-2");
  await expect(recentAttempts).toContainText("Succeeded");

  expect(harness.generatedBodies).toEqual([
    {
      voice_id: VOICE_ID,
      text: "Deliver one cutting line.",
      tone_preset: "cutting",
    },
    {
      voice_id: VOICE_ID,
      text: "Deliver one cutting line.",
      tone_preset: "cutting",
    },
  ]);
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

  await expect(page.locator('p[role="alert"]')).toContainText(BLOCKED_RIGHTS_MESSAGE);
});
