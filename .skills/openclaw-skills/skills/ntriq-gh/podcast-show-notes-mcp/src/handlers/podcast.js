/**
 * Podcast handlers for show notes generation
 * Calls ntriq AI server for audio summarization and analysis
 * Models: Whisper (MIT License) + Qwen (Apache 2.0 License)
 */

const SERVER = process.env.NTRIQ_AI_URL || "https://ai.ntriq.co.kr";
const DISCLAIMER =
  "AI-generated show notes. Not approved by or affiliated with podcast creator. For personal reference only. Do not redistribute without creator permission.";

async function callAudioServer(endpoint, body, timeout = 180) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), (timeout + 15) * 1000);

  try {
    const resp = await fetch(`${SERVER}/audio/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    clearTimeout(timer);

    if (!resp.ok) {
      const error = await resp.text();
      throw new Error(`Audio server error: ${resp.status} ${error}`);
    }

    return await resp.json();
  } catch (e) {
    clearTimeout(timer);
    throw e;
  }
}

export async function generateShowNotes(audioUrl, style = "detailed") {
  const result = await callAudioServer("summarize", {
    audio_url: audioUrl,
    summary_type: "detailed",
    max_tokens: 1500,
  });

  // Extract summary and key points
  const summary = result.summary || "";
  const sections =
    typeof summary === "string"
      ? [{ title: "Summary", content: summary }]
      : Array.isArray(summary)
        ? summary.map((item, idx) => ({
            title: item.title || `Section ${idx + 1}`,
            content: item.content || item,
          }))
        : [{ title: "Summary", content: JSON.stringify(summary) }];

  const keyTakeaways =
    result.key_takeaways ||
    extractTopLevelPoints(summary, style === "brief" ? 5 : 10);

  const topics = result.topics || [];

  return {
    status: "success",
    show_notes: {
      summary: summary.substring(0, 500),
      sections: sections.slice(0, style === "brief" ? 3 : undefined),
    },
    key_takeaways: keyTakeaways.slice(0, style === "brief" ? 5 : 10),
    topics: topics.slice(0, 8),
    style: style,
    disclaimer: DISCLAIMER,
    model: result.model || "whisper + qwen3.5",
  };
}

export async function generateChapters(audioUrl) {
  const result = await callAudioServer("analyze", {
    audio_url: audioUrl,
    max_tokens: 2048,
  });

  // Extract topics and generate chapters from analysis
  const topics = result.topics || [];
  const analysis = result.analysis || {};

  // Create chapter markers from identified topics
  const chapters = generateChapterMarkers(
    topics,
    analysis,
    result.duration || 3600,
  );

  return {
    status: "success",
    chapters: chapters,
    total_chapters: chapters.length,
    disclaimer: DISCLAIMER,
    model: result.model || "whisper + qwen3.5",
  };
}

export async function extractHighlights(audioUrl) {
  const result = await callAudioServer("summarize", {
    audio_url: audioUrl,
    summary_type: "action_items",
    max_tokens: 2000,
  });

  // Extract action items and key quotes
  const summary = result.summary || {};
  const actionItems =
    (typeof summary === "object" &&
      (summary.action_items || summary.actionItems)) ||
    [];
  const quotes = extractKeyQuotes(result.transcript || "", 8);
  const speakers = result.speakers_estimated || 1;

  return {
    status: "success",
    highlights: quotes.map((q) => ({
      quote: q.substring(0, 150),
      context: q.substring(0, 200),
    })),
    action_items: Array.isArray(actionItems) ? actionItems.slice(0, 10) : [],
    speakers_estimated: speakers,
    disclaimer: DISCLAIMER,
    model: result.model || "whisper + qwen3.5",
  };
}

// Helper: Extract key points from summary text
function extractTopLevelPoints(summary, limit = 5) {
  if (!summary) return [];
  if (typeof summary !== "string") return [];

  const lines = summary
    .split(/[\n•-]/)
    .map((l) => l.trim())
    .filter((l) => l.length > 10 && l.length < 200);

  return lines.slice(0, limit);
}

// Helper: Generate chapter markers from topics
function generateChapterMarkers(topics, analysis, totalDuration = 3600) {
  if (!Array.isArray(topics) || topics.length === 0) {
    return [
      {
        timestamp: "00:00:00",
        title: "Introduction",
      },
      {
        timestamp: formatTimestamp(totalDuration / 2),
        title: "Main Content",
      },
      {
        timestamp: formatTimestamp(Math.max(0, totalDuration - 300)),
        title: "Conclusion",
      },
    ];
  }

  const chapterCount = Math.min(topics.length, 8);
  const chapters = [];
  const intervalSeconds = totalDuration / (chapterCount + 1);

  topics.slice(0, chapterCount).forEach((topic, idx) => {
    const timestamp = formatTimestamp((idx + 1) * intervalSeconds);
    chapters.push({
      timestamp: timestamp,
      title:
        typeof topic === "string"
          ? topic.substring(0, 50)
          : topic.title || `Section ${idx + 1}`,
    });
  });

  return chapters;
}

// Helper: Format seconds to HH:MM:SS
function formatTimestamp(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// Helper: Extract key quotes from transcript (short excerpts only, no full text)
function extractKeyQuotes(transcript, limit = 8) {
  if (!transcript || typeof transcript !== "string") return [];

  const sentences = transcript
    .split(/[.!?]+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 15 && s.length < 200);

  const selected = [];
  const step = Math.max(1, Math.floor(sentences.length / limit));

  for (let i = 0; i < sentences.length && selected.length < limit; i += step) {
    selected.push(sentences[i]);
  }

  return selected;
}
