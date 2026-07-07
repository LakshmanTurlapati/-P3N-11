import { expect, type Locator, type Page, test } from "@playwright/test";

const LIVE_TEST_TIMEOUT_MS = 120_000;

const SPOKEN_TURN_AUDIO = Buffer.from("spoken-turn-audio");

async function tabUntilFocused(page: Page, target: Locator, maxTabs = 12) {
  for (let index = 0; index < maxTabs; index += 1) {
    await page.keyboard.press("Tab");

    if (await target.evaluate((element) => element === document.activeElement)) {
      return;
    }
  }

  throw new Error("Could not reach the expected control with keyboard navigation.");
}

async function installMediaRecorderMock(page: Page) {
  await page.addInitScript(() => {
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
        this.mimeType = options.mimeType ?? "audio/webm";
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
            data: new Blob([new Uint8Array([1, 2, 3, 4])], {
              type: this.mimeType,
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
  });
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

test("stopping a recording auto-posts a queued spoken turn and keeps it separate", async ({
  page,
}) => {
  await installMediaRecorderMock(page);
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
  await expect(spokenTurns).toContainText("Queued");
  await expect(recentAttempts).not.toContainText(audioTurnRecord.job_id);
  await expect(page.getByRole("button", { name: /transcribe/i })).toHaveCount(0);
});

test("uploading audio auto-posts a queued spoken turn and keeps it separate", async ({
  page,
}) => {
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
    name: "spoken-turn.webm",
    mimeType: "audio/webm",
    buffer: SPOKEN_TURN_AUDIO,
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
  await expect(spokenTurns).toContainText("Queued");
  await expect(recentAttempts).not.toContainText(audioTurnRecord.job_id);
});
