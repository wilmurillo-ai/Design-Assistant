#!/usr/bin/env node

const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");

const VERSION = "0.2.0";
const DEFAULT_API_BASE_URL = "http://127.0.0.1:8080";
const CONFIG_DIR = path.join(os.homedir(), ".openclaw", "invoice-skill");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");
const LEGACY_CONFIG_FILE = path.join(os.homedir(), ".openclaw", "invoice-plugin", "config.json");
const IMAGE_MAX_BYTES = 2 * 1024 * 1024;
const SUPPORTED_FORMATS = new Set(["json", "base64", "base64+json", "both"]);

function printJson(payload, exitCode = 0) {
  console.log(JSON.stringify(payload, null, 2));
  process.exitCode = exitCode;
}

function fail(message, extra = {}, exitCode = 1) {
  printJson(
    {
      ok: false,
      error: {
        message,
        ...extra
      }
    },
    exitCode
  );
}

function readJsonFile(filePath) {
  if (!fs.existsSync(filePath)) return {};
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return {};
  }
}

function readConfig() {
  const legacy = readJsonFile(LEGACY_CONFIG_FILE);
  const current = readJsonFile(CONFIG_FILE);
  return {
    ...legacy,
    ...current
  };
}

function writeConfig(next) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(next, null, 2), "utf8");
}

function clearStoredAppKey() {
  const current = readConfig();
  const next = { ...current };
  delete next.appKey;
  writeConfig(next);
  return next;
}

function getApiBaseUrl(config, override) {
  return override || config.apiBaseUrl || process.env.INVOICE_API_BASE_URL || DEFAULT_API_BASE_URL;
}

function randomId(prefix) {
  return `${prefix}${crypto.randomUUID().replace(/-/g, "")}`;
}

function ensurePersistentIds(config, options = {}) {
  return {
    clientInstanceId:
      options.clientInstanceId ||
      config.clientInstanceId ||
      process.env.OPENCLAW_CLIENT_INSTANCE_ID ||
      randomId("client_"),
    deviceFingerprint:
      options.deviceFingerprint ||
      config.deviceFingerprint ||
      process.env.OPENCLAW_DEVICE_FINGERPRINT ||
      randomId("device_")
  };
}

function buildHeaders(appKey, requestId) {
  const headers = {
    "Content-Type": "application/json"
  };
  if (requestId) {
    headers["X-Request-Id"] = requestId;
  }
  if (appKey) {
    headers.Authorization = `Bearer ${appKey}`;
  }
  return headers;
}

async function callApi(baseUrl, method, endpoint, body, appKey, requestId) {
  let response;
  try {
    response = await fetch(`${baseUrl}${endpoint}`, {
      method,
      headers: buildHeaders(appKey, requestId),
      body: body ? JSON.stringify(body) : undefined
    });
  } catch (error) {
    const detail =
      error && error.cause && error.cause.message ? error.cause.message : error.message;
    const wrapped = new Error(`request to ${baseUrl}${endpoint} failed: ${detail}`);
    wrapped.code = error && error.code ? error.code : "";
    throw wrapped;
  }

  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }

  if (!response.ok) {
    const message =
      (data && (data.message || data.msg || data.error)) || `HTTP ${response.status}`;
    const error = new Error(message);
    error.code = data && data.code ? String(data.code) : "";
    error.status = response.status;
    error.response = data;
    throw error;
  }

  return data;
}

function isInvalidAppKeyError(error) {
  const code = String(error && error.code ? error.code : "").toUpperCase();
  const message = String(error && error.message ? error.message : "").toLowerCase();
  return code === "INVALID_KEY" || code === "KEY_EXPIRED" || message.includes("invalid key");
}

async function initKey(options = {}) {
  const config = readConfig();
  const apiBaseUrl = getApiBaseUrl(config, options.apiBaseUrl);
  const ids = ensurePersistentIds(config, options);
  const clientInstanceId = options.rotateClientInstanceId ? randomId("client_") : ids.clientInstanceId;
  const deviceFingerprint = ids.deviceFingerprint;

  const response = await callApi(
    apiBaseUrl,
    "POST",
    "/api/v4/plugin/key/init",
    {
      clientInstanceId,
      deviceFingerprint,
      clientVersion: VERSION
    },
    null
  );

  const data = (response && response.data) || {};
  const appKey = data.key || response.key || "";
  const next = {
    ...config,
    apiBaseUrl,
    clientInstanceId,
    deviceFingerprint,
    cipherKey: data.cipherKey || config.cipherKey || null
  };
  if (appKey) {
    next.appKey = appKey;
  }
  writeConfig(next);

  return {
    ...next,
    autoBound: Boolean(appKey),
    initResponse: response
  };
}

async function withBoundConfig(handler, options = {}) {
  let bound = readConfig();
  bound.apiBaseUrl = getApiBaseUrl(bound, options.apiBaseUrl);

  if (!bound.appKey) {
    bound = await initKey(options);
  }

  try {
    return await handler(bound);
  } catch (error) {
    if (!isInvalidAppKeyError(error)) {
      throw error;
    }

    clearStoredAppKey();
    const rebound = await initKey({ ...options, rotateClientInstanceId: true });
    if (!rebound.appKey) {
      const message =
        "key init succeeded but backend did not return a usable key; clear local config or rotate clientInstanceId manually";
      const wrapped = new Error(message);
      wrapped.code = "KEY_REINIT_NO_KEY";
      wrapped.status = error && error.status ? error.status : null;
      throw wrapped;
    }
    return handler(rebound);
  }
}

function toHalfWidth(text) {
  return String(text || "")
    .replace(/\u3000/g, " ")
    .replace(/[\uff01-\uff5e]/g, (char) => String.fromCharCode(char.charCodeAt(0) - 0xfee0));
}

function pad2(value) {
  return String(value).padStart(2, "0");
}

function normalizeDate(year, month, day) {
  return `${year}-${pad2(month)}-${pad2(day)}`;
}

function normalizeInvoiceText(text) {
  return toHalfWidth(text)
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .replace(/[，；]/g, ",")
    .replace(/[：]/g, ":")
    .replace(/[（]/g, "(")
    .replace(/[）]/g, ")")
    .replace(/(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日?/g, (_, year, month, day) =>
      normalizeDate(year, month, day)
    )
    .replace(/(\d{4})[/.](\d{1,2})[/.](\d{1,2})/g, (_, year, month, day) =>
      normalizeDate(year, month, day)
    )
    .replace(/\n+/g, "\n")
    .replace(/[ \t]+/g, " ")
    .trim();
}

function escapeRegex(text) {
  return String(text || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function extractLabeledValue(text, labels, valuePattern) {
  for (const label of labels) {
    const pattern = new RegExp(
      `${escapeRegex(label)}\\s*(?:[:：]|是|为)?\\s*(${valuePattern})`,
      "i"
    );
    const match = text.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }
  return "";
}

function uniqueMatches(text, pattern) {
  return [...new Set(String(text || "").match(pattern) || [])];
}

function cleanupAmount(value) {
  const raw = String(value || "").replace(/,/g, "");
  const match = raw.match(/\d+(?:\.\d{1,2})?/);
  return match ? match[0] : "";
}

function extractInvoiceFields(text) {
  const normalizedText = normalizeInvoiceText(text);
  const fields = {
    invoiceCode: extractLabeledValue(
      normalizedText,
      ["发票代码", "代码", "invoice code", "invoicecode"],
      "[A-Za-z0-9]{10,12}"
    ),
    invoiceNumber: extractLabeledValue(
      normalizedText,
      ["发票号码", "号码", "票号", "invoice number", "invoicenumber"],
      "[A-Za-z0-9]{8,20}"
    ),
    billingDate: extractLabeledValue(
      normalizedText,
      ["开票日期", "日期", "invoice date", "billing date"],
      "\\d{4}-\\d{2}-\\d{2}"
    ),
    totalAmount: cleanupAmount(
      extractLabeledValue(
        normalizedText,
        ["不含税金额", "金额", "价税合计", "合计", "invoice amount", "total amount"],
        "\\d+(?:\\.\\d{1,2})?"
      )
    ),
    checkCode: extractLabeledValue(
      normalizedText,
      ["校验码", "校验码后6位", "check code", "checkcode"],
      "[A-Za-z0-9]{6,20}"
    )
  };

  if (!fields.invoiceCode) {
    fields.invoiceCode = uniqueMatches(normalizedText, /\b[A-Za-z0-9]{10,12}\b/g)[0] || "";
  }
  if (!fields.invoiceNumber) {
    const values = uniqueMatches(normalizedText, /\b[A-Za-z0-9]{8,20}\b/g).filter(
      (item) => item !== fields.invoiceCode
    );
    fields.invoiceNumber = values[0] || "";
  }
  if (!fields.billingDate) {
    fields.billingDate = uniqueMatches(normalizedText, /\b\d{4}-\d{2}-\d{2}\b/g)[0] || "";
  }
  if (!fields.totalAmount) {
    const amounts = uniqueMatches(normalizedText, /\b\d+(?:\.\d{1,2})\b/g).filter(
      (item) => item !== fields.invoiceCode && item !== fields.invoiceNumber
    );
    fields.totalAmount = cleanupAmount(amounts[0] || "");
  }

  return {
    normalizedText,
    fields
  };
}

function hasExtractedFields(fields) {
  return Boolean(
    fields &&
      (fields.invoiceCode ||
        fields.invoiceNumber ||
        fields.billingDate ||
        fields.totalAmount ||
        fields.checkCode)
  );
}

function normalizeResponseFormat(value) {
  const format = String(value || "json").toLowerCase();
  if (!SUPPORTED_FORMATS.has(format)) {
    throw new Error("format must be one of: json, base64, base64+json, both");
  }
  return format === "both" ? "base64+json" : format;
}

function maskAppKey(appKey) {
  if (!appKey) return null;
  if (appKey.length < 12) return appKey;
  return `${appKey.slice(0, 8)}****${appKey.slice(-4)}`;
}

function parseArgs(argv) {
  const positionals = [];
  const options = {};

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) {
      positionals.push(token);
      continue;
    }

    const key = token.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) {
      options[key] = true;
      continue;
    }

    options[key] = next;
    index += 1;
  }

  return { positionals, options };
}

function requireOption(options, key, message) {
  const value = options[key];
  if (value === undefined || value === null || value === "") {
    throw new Error(message);
  }
  return value;
}

function getMimeTypeFromPath(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  throw new Error("only .png, .jpg, and .jpeg are supported for image verification");
}

function stripDataUrlPrefix(value) {
  const text = String(value || "").trim();
  const match = text.match(/^data:(image\/[a-zA-Z0-9.+-]+);base64,(.+)$/s);
  if (match) {
    return {
      mimeType: match[1].toLowerCase(),
      base64: match[2]
    };
  }
  return {
    mimeType: "",
    base64: text
  };
}

function sanitizeBase64(value) {
  return String(value || "").replace(/\s+/g, "");
}

function estimateBase64Bytes(base64) {
  const clean = sanitizeBase64(base64);
  if (!clean) return 0;
  const padding = clean.endsWith("==") ? 2 : clean.endsWith("=") ? 1 : 0;
  return Math.floor((clean.length * 3) / 4) - padding;
}

function readImageInput(options) {
  if (options["image-file"]) {
    const filePath = path.resolve(String(options["image-file"]));
    if (!fs.existsSync(filePath)) {
      throw new Error(`image file not found: ${filePath}`);
    }
    const mimeType = options["mime-type"] || getMimeTypeFromPath(filePath);
    const buffer = fs.readFileSync(filePath);
    return {
      imageSource: "file",
      imagePath: filePath,
      mimeType,
      base64: buffer.toString("base64")
    };
  }

  if (options["image-base64"]) {
    const parsed = stripDataUrlPrefix(options["image-base64"]);
    return {
      imageSource: "base64",
      mimeType: String(options["mime-type"] || parsed.mimeType || "image/png").toLowerCase(),
      base64: sanitizeBase64(parsed.base64)
    };
  }

  throw new Error("verify-image requires --image-file or --image-base64");
}

function validateImagePayload(image) {
  if (!["image/png", "image/jpeg"].includes(image.mimeType)) {
    throw new Error("mime type must be image/png or image/jpeg");
  }
  if (!image.base64) {
    throw new Error("image content is empty");
  }
  const sizeBytes = estimateBase64Bytes(image.base64);
  if (sizeBytes > IMAGE_MAX_BYTES) {
    throw new Error("image must be 2MB or smaller");
  }
  return {
    ...image,
    sizeBytes
  };
}

function buildVerifyPayload(options, inputType, content) {
  const rawText = String(options.text || "").trim();
  const extracted = rawText
    ? extractInvoiceFields(rawText)
    : { normalizedText: "", fields: { invoiceCode: "", invoiceNumber: "", billingDate: "", totalAmount: "", checkCode: "" } };

  return {
    inputType,
    content,
    responseFormat: normalizeResponseFormat(options.format),
    invoiceCode: extracted.fields.invoiceCode,
    invoiceNumber: extracted.fields.invoiceNumber,
    billingDate: extracted.fields.billingDate,
    totalAmount: extracted.fields.totalAmount,
    checkCode: extracted.fields.checkCode,
    extracted
  };
}

async function runAction(action, options) {
  const apiBaseUrl = options["api-base-url"];

  if (action === "help") {
    return {
      ok: true,
      action,
      data: {
        commands: [
          "config show",
          "config set --api-base-url <url>",
          "config set --app-key <key>",
          "config clear-app-key",
          "init-key",
          "quota",
          "ledger [--page 1 --page-size 20]",
          "verify --text <invoice text> [--format json|base64|base64+json|both]",
          "verify-image --image-file <path> --text <invoice text>",
          "verify-image --image-base64 <base64> --text <invoice text>"
        ]
      }
    };
  }

  if (action === "config") {
    const configAction = options._subaction || "show";
    const current = readConfig();

    if (configAction === "show") {
      return {
        ok: true,
        action,
        data: {
          configFile: CONFIG_FILE,
          legacyConfigFile: LEGACY_CONFIG_FILE,
          apiBaseUrl: getApiBaseUrl(current),
          appKeyMasked: maskAppKey(current.appKey),
          clientInstanceId: current.clientInstanceId || null,
          deviceFingerprint: current.deviceFingerprint || null,
          cipherKey: current.cipherKey || null
        }
      };
    }

    if (configAction === "set") {
      const next = { ...current };
      if (options["api-base-url"]) next.apiBaseUrl = String(options["api-base-url"]);
      if (options["app-key"]) next.appKey = String(options["app-key"]);
      if (options["client-instance-id"]) next.clientInstanceId = String(options["client-instance-id"]);
      if (options["device-fingerprint"]) next.deviceFingerprint = String(options["device-fingerprint"]);
      writeConfig(next);
      return {
        ok: true,
        action,
        data: {
          configFile: CONFIG_FILE,
          apiBaseUrl: getApiBaseUrl(next),
          appKeyMasked: maskAppKey(next.appKey),
          clientInstanceId: next.clientInstanceId || null,
          deviceFingerprint: next.deviceFingerprint || null
        }
      };
    }

    if (configAction === "clear-app-key") {
      const next = clearStoredAppKey();
      return {
        ok: true,
        action,
        data: {
          configFile: CONFIG_FILE,
          apiBaseUrl: getApiBaseUrl(next),
          appKeyMasked: null,
          clientInstanceId: next.clientInstanceId || null,
          deviceFingerprint: next.deviceFingerprint || null
        }
      };
    }

    throw new Error("config subcommand must be show, set, or clear-app-key");
  }

  if (action === "init-key") {
    const result = await initKey({
      apiBaseUrl,
      clientInstanceId: options["client-instance-id"],
      deviceFingerprint: options["device-fingerprint"],
      rotateClientInstanceId: Boolean(options["rotate-client-instance-id"])
    });
    return {
      ok: true,
      action,
      data: result.initResponse,
      meta: {
        apiBaseUrl: result.apiBaseUrl,
        appKeyMasked: maskAppKey(result.appKey),
        clientInstanceId: result.clientInstanceId,
        deviceFingerprint: result.deviceFingerprint
      }
    };
  }

  return withBoundConfig(async (bound) => {
    if (action === "quota") {
      const response = await callApi(bound.apiBaseUrl, "GET", "/api/v4/plugin/quota", null, bound.appKey);
      return {
        ok: true,
        action,
        data: response,
        meta: {
          autoBound: bound.autoBound,
          apiBaseUrl: bound.apiBaseUrl
        }
      };
    }

    if (action === "ledger") {
      const page = Number(options.page || 1);
      const pageSize = Number(options["page-size"] || 20);
      const response = await callApi(
        bound.apiBaseUrl,
        "GET",
        `/api/v4/plugin/ledger?page=${encodeURIComponent(String(page))}&pageSize=${encodeURIComponent(String(pageSize))}`,
        null,
        bound.appKey
      );
      return {
        ok: true,
        action,
        data: response,
        meta: {
          autoBound: bound.autoBound,
          apiBaseUrl: bound.apiBaseUrl,
          page,
          pageSize
        }
      };
    }

    if (action === "verify") {
      const text = requireOption(options, "text", "verify requires --text");
      const payload = buildVerifyPayload(options, "text", text);
      const response = await callApi(
        bound.apiBaseUrl,
        "POST",
        "/api/v4/plugin/verify",
        payload,
        bound.appKey,
        crypto.randomUUID()
      );
      return {
        ok: true,
        action,
        data: response,
        meta: {
          autoBound: bound.autoBound,
          apiBaseUrl: bound.apiBaseUrl,
          extractedFields: payload.extracted.fields,
          normalizedText: payload.extracted.normalizedText
        }
      };
    }

    if (action === "verify-image") {
      const image = validateImagePayload(readImageInput(options));
      const payload = buildVerifyPayload(options, "image", image.base64);
      if (!hasExtractedFields(payload.extracted.fields)) {
        throw new Error("verify-image currently requires invoice fields in --text");
      }
      const response = await callApi(
        bound.apiBaseUrl,
        "POST",
        "/api/v4/plugin/verify",
        payload,
        bound.appKey,
        crypto.randomUUID()
      );
      return {
        ok: true,
        action,
        data: response,
        meta: {
          autoBound: bound.autoBound,
          apiBaseUrl: bound.apiBaseUrl,
          extractedFields: payload.extracted.fields,
          normalizedText: payload.extracted.normalizedText,
          image: {
            source: image.imageSource,
            path: image.imagePath || null,
            mimeType: image.mimeType,
            sizeBytes: image.sizeBytes
          }
        }
      };
    }

    throw new Error(`unsupported action: ${action}`);
  }, {
    apiBaseUrl,
    clientInstanceId: options["client-instance-id"],
    deviceFingerprint: options["device-fingerprint"]
  });
}

async function main() {
  const argv = process.argv.slice(2);
  const { positionals, options } = parseArgs(argv);
  const action = positionals[0] || "help";

  if (action === "config") {
    options._subaction = positionals[1] || "show";
  }

  const result = await runAction(action, options);
  printJson(result, result.ok ? 0 : 1);
}

main().catch((error) => {
  fail(error && error.message ? error.message : String(error), {
    code: error && error.code ? String(error.code) : "",
    status: error && error.status ? error.status : null,
    response: error && error.response ? error.response : null
  });
});
