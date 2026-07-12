import { expect, type Locator, type Page, test } from "@playwright/test";

const LIVE_TEST_TIMEOUT_MS = 120_000;

function buildWavBytes({
  sampleRateHz = 16_000,
  leadSilenceMs = 120,
  speechMs = 720,
  trailSilenceMs = 120,
  amplitude = 16_000,
}: {
  sampleRateHz?: number;
  leadSilenceMs?: number;
  speechMs?: number;
  trailSilenceMs?: number;
  amplitude?: number;
}): Buffer {
  const samples: number[] = [];
  for (const [durationMs, sampleValue] of [
    [leadSilenceMs, 0],
    [speechMs, amplitude],
    [trailSilenceMs, 0],
  ] as const) {
    const sampleCount = Math.max(Math.floor((sampleRateHz * durationMs) / 1000), 1);
    samples.push(...Array(sampleCount).fill(sampleValue));
  }

  const dataSize = samples.length * 2;
  const buffer = Buffer.alloc(44 + dataSize);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(1, 22);
  buffer.writeUInt32LE(sampleRateHz, 24);
  buffer.writeUInt32LE(sampleRateHz * 2, 28);
  buffer.writeUInt16LE(2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataSize, 40);

  samples.forEach((sample, index) => {
    buffer.writeInt16LE(sample, 44 + index * 2);
  });

  return buffer;
}

async function tabUntilFocused(page: Page, target: Locator, maxTabs = 12) {
  for (let index = 0; index < maxTabs; index += 1) {
    await page.keyboard.press("Tab");

    if (await target.evaluate((element) => element === document.activeElement)) {
      return;
    }
  }

  throw new Error("Could not reach the expected control with keyboard navigation.");
}

async function installMediaRecorderMock(page: Page, wavBytes: Buffer) {
  await page.addInitScript(
    ({ wavBytesBase64 }) => {
      class FakeMediaStreamTrack {
        kind = "audio";
        enabled = true;

        stop() {}
      }

      class FakeMediaStream {
        getTracks() {
          return [new FakeMediaStreamTrack()];
        }

        getAudioTracks() {
          return [new FakeMediaStreamTrack()];
        }
      }

      class FakeMediaRecorder {
        stream: MediaStream;
        state: "inactive" | "recording";
        mimeType: string;
        ondataavailable?: (event: { data: Blob }) => void;
        onstop?: (event: Event) => void;
        onstart?: (event: Event) => void;

        static isTypeSupported(type: string): boolean {
          return type === "audio/webm" || type === "audio/webm;codecs=opus";
        }

        constructor(stream: MediaStream, options: { mimeType?: string } = {}) {
          this.stream = stream;
          this.state = "inactive";
          this.mimeType = options.mimeType ? "audio/wav" : "audio/wav";
        }

        start(): void {
          this.state = "recording";
          if (typeof this.onstart === "function") {
            this.onstart(new Event("start"));
          }
        }

        stop(): void {
          this.state = "inactive";
          if (typeof this.ondataavailable === "function") {
            this.ondataavailable({
              data: new Blob([Uint8Array.from(atob(wavBytesBase64), (character) =>
                character.charCodeAt(0),
              )], {
                type: "audio/wav",
              }),
            });
          }
          if (typeof this.onstop === "function") {
            this.onstop(new Event("stop"));
          }
        }
      }

      Object.defineProperty(window.navigator, "mediaDevices", {
        configurable: true,
        value: {
          getUserMedia: async () => new FakeMediaStream(),
        },
      });

      Object.defineProperty(window, "MediaRecorder", {
        configurable: true,
        value: FakeMediaRecorder,
      });
    },
    {
      wavBytesBase64: wavBytes.toString("base64"),
    },
  );
}

async function waitForAudioTurnStatus(page: Page, jobId: string, expectedStatus: string) {
  await expect
    .poll(async () => {
      const response = await page.request.get(`/audio-turns/${jobId}`);
      const payload = (await response.json()) as { status?: string };
      return payload.status;
    })
    .toBe(expectedStatus);
}

test.describe.configure({ timeout: LIVE_TEST_TIMEOUT_MS });

test("spoken input controls are visible, labeled, and keyboard-focusable", async ({
  page,
}) => {
  await page.goto("/");

  const recordButton = page.getByRole("button", { name: "Record turn" });
  const uploadButton = page.getByRole("button", { name: "Upload audio" });
  const recordingStatus = page.getByRole("status", { name: "Recording status" });
  const recordingIndicator = page.getByLabel(/recording (timer|level)/i);

  await expect(recordButton).toBeVisible();
  await expect(uploadButton).toBeVisible();
  await expect(recordingStatus).toBeVisible();
  await expect(recordingIndicator).toBeVisible();

  await tabUntilFocused(page, recordButton);
  await expect(recordButton).toBeFocused();
  await expect(recordButton).toHaveCSS("outline-style", "solid");

  await tabUntilFocused(page, uploadButton);
  await expect(uploadButton).toBeFocused();
  await expect(uploadButton).toHaveCSS("outline-style", "solid");
});

test("stopping a recording auto-posts a queued spoken turn and exposes VAD metadata", async ({
  page,
}) => {
  const recordedWav = buildWavBytes({ amplitude: 16_000, speechMs: 720 });
  await installMediaRecorderMock(page, recordedWav);
  await page.goto("/");

  const recordButton = page.getByRole("button", { name: "Record turn" });
  const stopButton = page.getByRole("button", { name: "Stop recording" });
  const spokenTurns = page.getByRole("list", { name: "Spoken turns" });
  const recentAttempts = page.getByRole("list", { name: "Recent attempts" });
  const recordingStatus = page.getByRole("status", { name: "Recording status" });
  const recordingIndicator = page.getByLabel(/recording (timer|level)/i);

  await expect(spokenTurns).toContainText("No spoken turns yet");
  await expect(recentAttempts).toBeVisible();

  await recordButton.click();
  await expect(recordingStatus).toContainText("Recording...");
  await expect(recordingIndicator).toBeVisible();
  await expect(stopButton).toBeVisible();

  const audioTurnResponsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().endsWith("/audio-turns") &&
      response.status() === 200,
  );

  await stopButton.click();

  const audioTurnResponse = await audioTurnResponsePromise;
  const audioTurnRecord = (await audioTurnResponse.json()) as {
    job_id: string;
    status: string;
  };

  expect(audioTurnRecord.status).toBe("queued");
  expect(typeof audioTurnRecord.job_id).toBe("string");
  expect(audioTurnRecord.job_id.length).toBeGreaterThan(0);

  await expect(recordingStatus).toContainText("Queued");
  await expect(spokenTurns).toContainText(audioTurnRecord.job_id);
  await expect(spokenTurns).toContainText("Silero VAD");
  await expect(spokenTurns).toContainText("Speech range");
  await expect(spokenTurns).toContainText("Speech duration");
  await expect(spokenTurns).toContainText("Confidence");
  await expect(recentAttempts).not.toContainText(audioTurnRecord.job_id);
  await expect(page.getByRole("button", { name: /transcribe/i })).toHaveCount(0);
});

test("uploading audio exposes a weak-turn warning and keeps it separate", async ({
  page,
}) => {
  const thinWav = buildWavBytes({ amplitude: 900, speechMs: 160 });
  await page.goto("/");

  const uploadButton = page.getByRole("button", { name: "Upload audio" });
  const spokenTurns = page.getByRole("list", { name: "Spoken turns" });
  const recentAttempts = page.getByRole("list", { name: "Recent attempts" });
  const recordingStatus = page.getByRole("status", { name: "Recording status" });

  await expect(uploadButton).toBeVisible();

  const audioTurnResponsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().endsWith("/audio-turns") &&
      response.status() === 200,
  );

  await page.locator('input[type="file"]').setInputFiles({
    name: "thin-turn.wav",
    mimeType: "audio/wav",
    buffer: thinWav,
  });

  const audioTurnResponse = await audioTurnResponsePromise;
  const audioTurnRecord = (await audioTurnResponse.json()) as {
    job_id: string;
    status: string;
  };

  expect(audioTurnRecord.status).toBe("queued");
  expect(typeof audioTurnRecord.job_id).toBe("string");
  expect(audioTurnRecord.job_id.length).toBeGreaterThan(0);

  await expect(recordingStatus).toContainText("Queued");
  await expect(spokenTurns).toContainText(audioTurnRecord.job_id);
  await expect(spokenTurns).toContainText("Silero VAD");
  await expect(spokenTurns).toContainText("thin or low-confidence");
  await expect(spokenTurns).toContainText("Speech range");
  await expect(spokenTurns).toContainText("Speech duration");
  await expect(spokenTurns).toContainText("Confidence");
  await expect(recentAttempts).not.toContainText(audioTurnRecord.job_id);
});

test("transcript review stays editable and only copies into the composer on demand", async ({
  page,
}) => {
  const speechWav = buildWavBytes({ amplitude: 16_000, speechMs: 720 });
  await page.goto("/");

  const generationText = page.getByRole("textbox", { name: "Generation text" });
  const spokenTurns = page.getByRole("list", { name: "Spoken turns" });

  const audioTurnResponsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().endsWith("/audio-turns") &&
      response.status() === 200,
  );

  await page.locator('input[type="file"]').setInputFiles({
    name: "spoken-turn.wav",
    mimeType: "audio/wav",
    buffer: speechWav,
  });

  const audioTurnResponse = await audioTurnResponsePromise;
  const audioTurnRecord = (await audioTurnResponse.json()) as {
    job_id: string;
    status: string;
  };

  expect(audioTurnRecord.status).toBe("queued");
  await waitForAudioTurnStatus(page, audioTurnRecord.job_id, "succeeded");

  const spokenTurnCard = spokenTurns
    .locator("article")
    .filter({
      has: page.getByRole("heading", { name: audioTurnRecord.job_id }),
    })
    .first();
  const transcriptField = spokenTurnCard.getByRole("textbox", {
    name: "Transcript review",
  });
  const useAsGenerationTextButton = spokenTurnCard.getByRole("button", {
    name: "Use as generation text",
  });

  await expect(transcriptField).toBeVisible();
  await expect(transcriptField).toBeEditable();
  await expect(useAsGenerationTextButton).toBeEnabled();
  await expect(generationText).toHaveValue("");

  const originalTranscript = await transcriptField.inputValue();
  expect(originalTranscript.length).toBeGreaterThan(0);
  const reviewedTranscript = `${originalTranscript} with one theatrical edit`;

  await transcriptField.fill(reviewedTranscript);
  await expect(transcriptField).toHaveValue(reviewedTranscript);

  await expect(generationText).toHaveValue("");

  await useAsGenerationTextButton.click();

  await expect(generationText).toHaveValue(reviewedTranscript);
});
