import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
  webServer: [
    {
      command:
        "cd ../.. && THEATRICAL_VOICE_STUDIO_PLAYWRIGHT=1 THEATRICAL_VOICE_STUDIO_VAD_FIXTURE=1 THEATRICAL_VOICE_STUDIO_STT_FIXTURE=1 .venv/bin/python -m uvicorn services.api.app.main:app --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/voices",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command:
        "API_BASE_URL=http://127.0.0.1:8000 pnpm exec next build && API_BASE_URL=http://127.0.0.1:8000 pnpm exec next start --hostname 127.0.0.1 --port 3000",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
