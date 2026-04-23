/**
 * Podcast Show Notes MCP Server
 * Generate show notes, chapters, and highlights from podcast audio
 * Main entry point for Apify Actor
 */

import { Actor } from "apify";
import { trackMCP } from "agnost";
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

import {
  generateShowNotes,
  generateChapters,
  extractHighlights,
} from "./handlers/podcast.js";

// PPE charge amounts per tool — MUST match pay_per_event.json exactly
const CHARGE_MAP = {
  generate_show_notes: 0.1,
  generate_chapters: 0.08,
  extract_highlights: 0.12,
};

async function main() {
  await Actor.init();

  const app = express();
  app.use(express.json());

  const mcpServer = new McpServer({
    name: "podcast-show-notes-mcp",
    version: "1.0.0",
  });

  // --- Register 3 MCP Tools ---

  mcpServer.tool(
    "generate_show_notes",
    "Generate podcast show notes with key takeaways from audio. Returns structured summary (no full transcript).",
    {
      audioUrl: z.string().describe("URL of the podcast audio file to analyze"),
      style: z
        .enum(["brief", "detailed"])
        .optional()
        .describe(
          "Show notes style: brief (3-5 key takeaways), detailed (sections with summary) — default: detailed",
        ),
    },
    async ({ audioUrl, style }) => {
      const result = await generateShowNotes(audioUrl, style || "detailed");
      await chargeForTool("generate_show_notes");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "generate_chapters",
    "Generate timestamped chapter markers for podcast audio. Returns chapters with timestamps.",
    {
      audioUrl: z.string().describe("URL of the podcast audio file to analyze"),
    },
    async ({ audioUrl }) => {
      const result = await generateChapters(audioUrl);
      await chargeForTool("generate_chapters");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "extract_highlights",
    "Extract key quotes and highlights from podcast audio. Returns key quotes (short excerpts) and action items (no full transcript).",
    {
      audioUrl: z.string().describe("URL of the podcast audio file to analyze"),
    },
    async ({ audioUrl }) => {
      const result = await extractHighlights(audioUrl);
      await chargeForTool("extract_highlights");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  // --- MCP Transport ---

  trackMCP(mcpServer, "podcast-show-notes-mcp-unique-id");

  app.post("/mcp", async (req, res) => {
    try {
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
      });
      res.on("close", () => transport.close());
      await mcpServer.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("MCP request error:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: {
            code: -32603,
            message: error.message || "Internal server error",
          },
          id: null,
        });
      }
    }
  });

  app.get("/health", (req, res) => {
    res.json({
      status: "ok",
      server: "podcast-show-notes-mcp",
      version: "1.0.0",
    });
  });

  const port = process.env.APIFY_CONTAINER_PORT || 3000;
  app.listen(port, "0.0.0.0", () => {
    console.log(
      `Podcast Show Notes MCP Server listening on http://0.0.0.0:${port}/mcp`,
    );
  });
}

async function chargeForTool(toolName) {
  const amount = CHARGE_MAP[toolName];
  if (amount) {
    try {
      await Actor.charge({ eventName: toolName, count: 1 });
      console.log(`Charged $${amount} for ${toolName}`);
    } catch (e) {
      console.error(`Charge failed for ${toolName}:`, e.message);
    }
  }
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
