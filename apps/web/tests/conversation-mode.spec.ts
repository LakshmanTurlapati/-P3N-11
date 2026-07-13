import { expect, test } from "@playwright/test";

const LIVE_TEST_TIMEOUT_MS = 120_000;
const CONVERSATION_SESSION_ID = "conversation-session-001";

function buildConversationSessionRecord(status: "listening" | "stopped") {
  return {
    session_id: CONVERSATION_SESSION_ID,
    status,
    turns: [],
  };
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
