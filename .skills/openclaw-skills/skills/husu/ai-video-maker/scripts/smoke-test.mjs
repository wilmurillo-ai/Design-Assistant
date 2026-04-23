#!/usr/bin/env node
import { createAIVideoClient } from "./aivideo-client.mjs";

function print(data) {
  // eslint-disable-next-line no-console
  console.log(JSON.stringify(data, null, 2));
}

async function testGetStatus(client, taskId) {
  const result = await client.getStatus(taskId);
  return {
    case: "getStatus",
    pass: typeof result?.ok === "boolean" && typeof result?.status === "string",
    result,
  };
}

async function testGetTask(client, taskId) {
  const result = await client.getTask(taskId);
  return {
    case: "getTask",
    pass: typeof result?.ok === "boolean" && "data" in result,
    result,
  };
}

async function testCancelTask(client, taskId) {
  const result = await client.cancelTask(taskId);
  return {
    case: "cancelTask",
    pass: typeof result?.ok === "boolean" && typeof result?.status === "string",
    result,
  };
}

async function main() {
  const taskId = process.env.SMOKE_TASK_ID;
  if (!taskId) {
    throw new Error("SMOKE_TASK_ID is required for smoke test");
  }

  const client = createAIVideoClient({ debug: false });
  const checks = [];

  checks.push(await testGetStatus(client, taskId));
  checks.push(await testGetTask(client, taskId));
  checks.push(await testCancelTask(client, taskId));

  const passCount = checks.filter((c) => c.pass).length;
  const summary = {
    passCount,
    total: checks.length,
    pass: passCount === checks.length,
  };

  print({ summary, checks });

  if (!summary.pass) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  print({
    summary: { pass: false },
    error: error?.message || "Smoke test failed",
  });
  process.exitCode = 1;
});
