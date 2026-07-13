import { expect, type Page, test } from "@playwright/test";

const LIVE_TEST_TIMEOUT_MS = 120_000;
const CONVERSATION_SESSION_ID = "conversation-session-001";
const CONVERSATION_TURN_ID = "conversation-turn-001";
const CONVERSATION_TURN_AUDIO_URL = `/conversation-turns/${CONVERSATION_TURN_ID}/audio`;
const CONVERSATION_TURN_LATENCY_CHIP_TEXT = "1.24 s";
const RESPONSE_TEXT =
  "Well. That was almost interesting. Almost.";

type ConversationTonePreset = "measured" | "cutting" | "grandiose";

type ConversationTurnStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "interrupted"
  | "canceled";

type ConversationTurnRecord = {
  turn_id: string;
  status: ConversationTurnStatus;
  input_audio_url: string | null;
  user_transcript_text: string | null;
  response_text: string | null;
  playback_url: string | null;
  tone_preset: ConversationTonePreset | null;
  latency_ms: number | null;
  cancel_state: ConversationTurnCancelState | null;
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
    speech_end_to_transcript_ms: number | null;
    response_text_ms: number | null;
    tts_complete_ms: number | null;
    playback_start_ms: number | null;
  };
};

type ConversationTurnCancelState = {
  requested_at: string;
  interrupted_at: string | null;
  canceled_at: string | null;
  reason: string | null;
};

function buildConversationSessionRecord(
  status: "listening" | "stopped",
  turns: ConversationTurnRecord[] = [],
) {
  return {
    session_id: CONVERSATION_SESSION_ID,
    status,
    turns,
    timing: {
      started_at: "2026-07-12T03:00:00.000Z",
      ended_at: "2026-07-12T03:00:00.000Z",
      duration_ms: 0,
    },
  };
}

function buildConversationTurnRecord(
  status: ConversationTurnStatus,
  overrides: Partial<ConversationTurnRecord> = {},
) {
  const baseRecord: ConversationTurnRecord = {
    turn_id: CONVERSATION_TURN_ID,
    status,
    input_audio_url: `/conversation-turns/${CONVERSATION_TURN_ID}/input.wav`,
    user_transcript_text:
      status === "succeeded" ? "The line is ready." : "Pending transcript.",
    response_text: status === "succeeded" ? RESPONSE_TEXT : null,
    playback_url: status === "succeeded" ? CONVERSATION_TURN_AUDIO_URL : null,
    tone_preset: status === "succeeded" ? "cutting" : null,
    latency_ms: status === "succeeded" ? 1240 : null,
    cancel_state:
      status === "interrupted" || status === "canceled"
        ? {
            requested_at: "2026-07-12T03:00:02.050Z",
            interrupted_at: status === "interrupted" ? "2026-07-12T03:00:02.120Z" : null,
            canceled_at: status === "canceled" ? "2026-07-12T03:00:02.120Z" : null,
            reason: "manual interrupt",
          }
        : null,
    timing: {
      started_at: "2026-07-12T03:00:01.000Z",
      ended_at: "2026-07-12T03:00:02.240Z",
      duration_ms: status === "succeeded" ? 1240 : 0,
      speech_end_to_transcript_ms: status === "succeeded" ? 180 : null,
      response_text_ms: status === "succeeded" ? 420 : null,
      tts_complete_ms: status === "succeeded" ? 940 : null,
      playback_start_ms: status === "succeeded" ? 1240 : null,
    },
  };

  return {
    ...baseRecord,
    ...overrides,
  };
}

async function installAudioPauseSpy(page: Page) {
  await page.addInitScript(() => {
    const originalPause = HTMLMediaElement.prototype.pause;
    (window as Window & { __pauseCalls?: number }).__pauseCalls = 0;
    HTMLMediaElement.prototype.pause = function pause(this: HTMLMediaElement) {
      const globalWindow = window as Window & { __pauseCalls?: number };
      globalWindow.__pauseCalls = (globalWindow.__pauseCalls ?? 0) + 1;
      return originalPause.call(this);
    };
  });
}

async function installConversationBargeInMock(page: Page) {
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

    class FakeAnalyserNode {
      fftSize = 256;

      connect() {}

      disconnect() {}

      getByteTimeDomainData(samples: Uint8Array) {
        samples.fill(240);
      }
    }

    class FakeMediaStreamSource {
      connect() {}

      disconnect() {}
    }

    class FakeAudioContext {
      state: "running" | "suspended" | "closed" = "running";

      resume() {
        this.state = "running";
        return Promise.resolve();
      }

      close() {
        this.state = "closed";
        return Promise.resolve();
      }

      createAnalyser() {
        return new FakeAnalyserNode();
      }

      createMediaStreamSource(_stream: MediaStream) {
        return new FakeMediaStreamSource();
      }
    }

    Object.defineProperty(window.navigator, "mediaDevices", {
      configurable: true,
      value: {
        getUserMedia: async () => new FakeMediaStream(),
      },
    });

    Object.defineProperty(window, "AudioContext", {
      configurable: true,
      value: FakeAudioContext,
    });
  });
}

async function armConversationPlayback(
  page: Page,
  turnId: string,
  pauseCallsLabel = "__pauseCalls",
) {
  await page
    .getByLabel(`Conversation turn ${turnId} playback`)
    .evaluate((audio, pauseCallsLabelValue: string) => {
      let playing = false;

      Object.defineProperty(audio, "paused", {
        configurable: true,
        get: () => !playing,
      });

      Object.defineProperty(audio, "ended", {
        configurable: true,
        get: () => false,
      });

      Object.defineProperty(audio, "play", {
        configurable: true,
        value: () => {
          playing = true;
          return Promise.resolve();
        },
      });

      Object.defineProperty(audio, "pause", {
        configurable: true,
        value: () => {
          playing = false;
          const globalWindow = window as Window & { __pauseCalls?: number };
          globalWindow[pauseCallsLabelValue as string] =
            (globalWindow[pauseCallsLabelValue as string] ?? 0) + 1;
        },
      });

      return audio.play();
    }, pauseCallsLabel);
}

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
} = {}): Buffer {
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
              data: new Blob(
                [
                  Uint8Array.from(atob(wavBytesBase64), (character) =>
                    character.charCodeAt(0),
                  ),
                ],
                {
                  type: "audio/wav",
                },
              ),
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

test.describe.configure({ timeout: LIVE_TEST_TIMEOUT_MS });

test("start conversation keeps the live panel inline on /", async ({ page }) => {
  const startRequests: Array<{
    url: string;
    method: string;
    body: string | null;
  }> = [];
  const stopRequests: Array<{
    url: string;
    method: string;
    body: string | null;
  }> = [];
  let sessionStatus: "listening" | "stopped" = "listening";

  await page.route("**/conversation-sessions", async (route) => {
    startRequests.push({
      url: route.request().url(),
      method: route.request().method(),
      body: route.request().postData(),
    });
    await route.fulfill({
      contentType: "application/json",
      json: buildConversationSessionRecord("listening"),
    });
  });

  await page.route("**/conversation-sessions/conversation-session-001", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      json: buildConversationSessionRecord(sessionStatus),
    });
  });

  await page.route("**/conversation-sessions/conversation-session-001/stop", async (route) => {
    stopRequests.push({
      url: route.request().url(),
      method: route.request().method(),
      body: route.request().postData(),
    });
    sessionStatus = "stopped";
    await route.fulfill({
      contentType: "application/json",
      json: buildConversationSessionRecord("stopped"),
    });
  });

  await page.goto("/");

  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(page.getByRole("heading", { name: "Live conversation" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Start conversation" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Stop conversation" })).toBeVisible();
  await expect(page.getByRole("list", { name: "Conversation turns" })).toBeVisible();
  await expect(page.getByRole("list", { name: "Conversation turns" })).toContainText(
    "No conversation turns yet.",
  );

  await page.getByRole("button", { name: "Start conversation" }).click();

  await expect(page.getByRole("status", { name: "Live conversation status" })).toContainText(
    "Listening",
  );

  expect(startRequests).toHaveLength(1);
  expect(startRequests[0]).toMatchObject({
    url: "http://127.0.0.1:3000/conversation-sessions",
    method: "POST",
    body: null,
  });

  await page.getByRole("button", { name: "Stop conversation" }).click();

  await expect(page.getByRole("status", { name: "Live conversation status" })).toContainText(
    "Stopped",
  );

  expect(stopRequests).toHaveLength(1);
  expect(stopRequests[0]).toMatchObject({
    url: "http://127.0.0.1:3000/conversation-sessions/conversation-session-001/stop",
    method: "POST",
    body: null,
  });
});

test("response playback shows up in the live conversation turn card", async ({
  page,
}) => {
  const recordingWav = buildWavBytes();
  await installMediaRecorderMock(page, recordingWav);

  let sessionRecord = buildConversationSessionRecord("listening");

  await page.route("**/conversation-sessions", async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }

    await route.fulfill({
      contentType: "application/json",
      json: sessionRecord,
    });
  });

  await page.route(`**/conversation-sessions/${CONVERSATION_SESSION_ID}`, async (route) => {
    await route.fulfill({
      contentType: "application/json",
      json: sessionRecord,
    });
  });

  await page.route("**/conversation-turns", async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }

    expect(route.request().headers()["x-conversation-session-id"]).toBe(
      CONVERSATION_SESSION_ID,
    );
    expect(route.request().headers()["x-audio-capture-source"]).toBe("recording");
    expect(route.request().headers()["x-voice-id"]).toBe("vesper-glass");
    expect(route.request().headers()["x-tone-preset"]).toBe("cutting");

    sessionRecord = buildConversationSessionRecord("listening", [
      buildConversationTurnRecord("queued", {
        response_text: null,
        playback_url: null,
        latency_ms: null,
      }),
    ]);

    await route.fulfill({
      contentType: "application/json",
      json: buildConversationTurnRecord("queued", {
        response_text: null,
        playback_url: null,
        latency_ms: null,
      }),
    });
  });

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}`,
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        json: buildConversationTurnRecord("succeeded"),
      });
    },
  );

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}/audio`,
    async (route) => {
      await route.fulfill({
        contentType: "audio/wav",
        body: recordingWav,
      });
    },
  );

  await page.goto("/");

  await expect(page.getByRole("button", { name: "Cutting" })).toBeVisible();
  await page.getByRole("button", { name: "Cutting" }).click();

  await page.getByRole("button", { name: "Start conversation" }).click();
  await expect(page.getByRole("status", { name: "Live conversation status" })).toContainText(
    "Listening",
  );

  await page.getByRole("button", { name: "Record turn" }).click();

  const conversationTurnResponsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      response.url().endsWith("/conversation-turns") &&
      response.status() === 200,
    {
      timeout: 5_000,
    },
  );

  await page.getByRole("button", { name: "Stop recording" }).click();

  const conversationTurnResponse = await conversationTurnResponsePromise;
  const conversationTurnRecord = (await conversationTurnResponse.json()) as {
    turn_id: string;
    status: ConversationTurnStatus;
  };

  expect(conversationTurnRecord.turn_id).toBe(CONVERSATION_TURN_ID);
  expect(conversationTurnRecord.status).toBe("queued");

  sessionRecord = buildConversationSessionRecord("listening", [
    buildConversationTurnRecord("succeeded"),
  ]);

  await expect(page.getByRole("list", { name: "Conversation turns" })).toContainText(
    RESPONSE_TEXT,
  );
  await expect(
    page.getByLabel(`Conversation turn ${CONVERSATION_TURN_ID} latency chip`),
  ).toHaveText(CONVERSATION_TURN_LATENCY_CHIP_TEXT);
  await expect(page.getByLabel(`Conversation turn ${CONVERSATION_TURN_ID} playback`)).toHaveAttribute(
    "src",
    new RegExp(`${CONVERSATION_TURN_AUDIO_URL}$`),
  );
});

test("interrupt control pauses playback and returns the panel to listening", async ({
  page,
}) => {
  await installAudioPauseSpy(page);

  let sessionRecord = buildConversationSessionRecord("listening", [
    buildConversationTurnRecord("succeeded"),
  ]);
  const interruptRequests: Array<{
    url: string;
    method: string;
    body: string | null;
  }> = [];

  await page.route("**/conversation-sessions", async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }

    await route.fulfill({
      contentType: "application/json",
      json: sessionRecord,
    });
  });

  await page.route(`**/conversation-sessions/${CONVERSATION_SESSION_ID}`, async (route) => {
    await route.fulfill({
      contentType: "application/json",
      json: sessionRecord,
    });
  });

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}/interrupt`,
    async (route) => {
      interruptRequests.push({
        url: route.request().url(),
        method: route.request().method(),
        body: route.request().postData(),
      });

      sessionRecord = buildConversationSessionRecord("listening", [
        buildConversationTurnRecord("interrupted"),
      ]);

      await route.fulfill({
        contentType: "application/json",
        json: buildConversationTurnRecord("interrupted"),
      });
    },
  );

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}`,
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        json: buildConversationTurnRecord("interrupted"),
      });
    },
  );

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}/audio`,
    async (route) => {
      await route.fulfill({
        contentType: "audio/wav",
        body: buildWavBytes(),
      });
    },
  );

  await page.goto("/");

  await expect(page.getByRole("button", { name: "Start conversation" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Interrupt" })).toBeVisible();

  await page.getByRole("button", { name: "Interrupt" }).click();

  await expect.poll(async () =>
    page.evaluate(() => (window as Window & { __pauseCalls?: number }).__pauseCalls ?? 0),
  ).toBeGreaterThan(0);

  expect(interruptRequests).toHaveLength(1);
  expect(interruptRequests[0]).toMatchObject({
    url: "http://127.0.0.1:3000/conversation-turns/conversation-turn-001/interrupt",
    method: "POST",
    body: null,
  });

  await expect(page.getByRole("status", { name: "Live conversation status" })).toContainText(
    "Listening",
  );
  await expect(page.getByRole("list", { name: "Conversation turns" })).toContainText(
    /Interrupted|Canceled/,
  );
});

test("speech-triggered barge-in pauses playback and posts the interrupt route", async ({
  page,
}) => {
  await installAudioPauseSpy(page);
  await installConversationBargeInMock(page);

  let sessionRecord = buildConversationSessionRecord("listening", [
    buildConversationTurnRecord("succeeded"),
  ]);
  const interruptRequests: Array<{
    url: string;
    method: string;
    body: string | null;
  }> = [];

  await page.route("**/conversation-sessions", async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }

    await route.fulfill({
      contentType: "application/json",
      json: sessionRecord,
    });
  });

  await page.route(`**/conversation-sessions/${CONVERSATION_SESSION_ID}`, async (route) => {
    await route.fulfill({
      contentType: "application/json",
      json: sessionRecord,
    });
  });

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}/interrupt`,
    async (route) => {
      interruptRequests.push({
        url: route.request().url(),
        method: route.request().method(),
        body: route.request().postData(),
      });

      sessionRecord = buildConversationSessionRecord("listening", [
        buildConversationTurnRecord("interrupted"),
      ]);

      await route.fulfill({
        contentType: "application/json",
        json: buildConversationTurnRecord("interrupted"),
      });
    },
  );

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}`,
    async (route) => {
      await route.fulfill({
        contentType: "application/json",
        json: buildConversationTurnRecord("succeeded"),
      });
    },
  );

  await page.route(
    `**/conversation-turns/${CONVERSATION_TURN_ID}/audio`,
    async (route) => {
      await route.fulfill({
        contentType: "audio/wav",
        body: buildWavBytes(),
      });
    },
  );

  await page.goto("/");

  await expect(page.getByRole("button", { name: "Interrupt" })).toBeVisible();
  await page.getByRole("button", { name: "Start conversation" }).click();
  await expect(page.getByRole("status", { name: "Live conversation status" })).toContainText(
    "Listening",
  );

  await armConversationPlayback(page, CONVERSATION_TURN_ID);

  await expect.poll(async () =>
    page.evaluate(() => (window as Window & { __pauseCalls?: number }).__pauseCalls ?? 0),
  ).toBeGreaterThan(0);

  expect(interruptRequests).toHaveLength(1);
  expect(interruptRequests[0]).toMatchObject({
    url: "http://127.0.0.1:3000/conversation-turns/conversation-turn-001/interrupt",
    method: "POST",
    body: null,
  });

  await expect(page.getByRole("status", { name: "Live conversation status" })).toContainText(
    "Listening",
  );
  await expect(page.getByRole("list", { name: "Conversation turns" })).toContainText(
    /Interrupted|Canceled/,
  );
});
