// services/botService.js
import axios from "axios";
import FormData from "form-data";
import fs from "fs";

const BOT_URL = process.env.PYTHON_BOT_URL || "http://localhost:8000"; // e.g. http://localhost:8000
const BOT_API_KEY = process.env.BOT_API_KEY || ""; // optional server-to-server auth
const TIMEOUT = parseInt(process.env.REQUEST_TIMEOUT_MS || "20000", 10);

// Helper to get headers including optional auth
function makeHeaders(additional = {}) {
  const h = { "Content-Type": "application/json", ...additional };
  if (BOT_API_KEY) h["Authorization"] = `Bearer ${BOT_API_KEY}`;
  return h;
}

/**
 * sendMessage(payload)
 * payload: { userId?, message, sessionId?, language? }
 * returns normalized object: { answer, confidence, needsHuman, language, sources, raw }
 */
async function sendMessage(payload) {
  try {
    const res = await axios.post(
      `${BOT_URL}/api/ask`,
      { question: payload.message, session_id: payload.sessionId, userId: payload.userId, language: payload.language },
      { timeout: TIMEOUT, headers: makeHeaders() }
    );

    // Accept either { success, answer, confidence, ... } OR nested shapes
    const data = res.data || {};
    // Many implementations return { success, question, answer, intent, confidence, entities, sources }
    // Normalize common fields safely:
    const answer = data.answer ?? data.result ?? data.reply ?? "";
    const confidence = (data.confidence !== undefined) ? Number(data.confidence) : (data.score !== undefined ? Number(data.score) : 0);
    const needsHuman = data.needsHuman ?? data.needs_human ?? false;
    const language = data.language ?? payload.language ?? data.lang;
    const sources = data.sources ?? data.source_documents ?? [];

    return { answer, confidence, needsHuman, language, sources, raw: data };
  } catch (err) {
    // If axios has response body, include it for debugging
    const status = err.response?.status;
    const body = err.response?.data;
    console.error("botService.sendMessage error:", err.message, "status:", status, "body:", body);
    // Throw a descriptive error so controller's try/catch can forward it to middleware
    throw new Error(`Bot service unreachable${status ? ` (status ${status})` : ""}${body ? `: ${JSON.stringify(body)}` : ""}`);
  }
}

/**
 * ingestFile(filePath, filename, meta = {})
 * Uploads file to python ingest endpoint (multipart/form-data)
 */
async function ingestFile(filePath, filename, meta = {}) {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath), filename);
  form.append("meta", JSON.stringify(meta));

  try {
    const res = await axios.post(`${BOT_URL}/api/upload-faq`, form, {
      headers: { ...form.getHeaders(), ...(BOT_API_KEY ? { Authorization: `Bearer ${BOT_API_KEY}` } : {}) },
      timeout: 5 * 60_000,
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });
    return res.data;
  } catch (err) {
    console.error("botService.ingestFile error:", err.message, err.response?.data);
    throw new Error("Ingest failed: " + (err.response?.data?.error ?? err.message));
  }
}

// default export matches your controller import: `import botService from "../services/botService.js";`
export default { sendMessage, ingestFile };
