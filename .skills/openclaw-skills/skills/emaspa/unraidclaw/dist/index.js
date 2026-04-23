// src/client.ts
import { request as httpsRequest, Agent as HttpsAgent } from "https";
import { request as httpRequest } from "http";
var UnraidApiError = class extends Error {
  constructor(message, statusCode, errorCode) {
    super(message);
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.name = "UnraidApiError";
  }
};
var UnraidClient = class {
  configResolver;
  insecureAgent = null;
  constructor(configResolver) {
    this.configResolver = configResolver;
  }
  getConfig() {
    const cfg = this.configResolver();
    if (!cfg.serverUrl) {
      throw new UnraidApiError("UnraidClaw serverUrl not configured", 0, "CONFIG_ERROR");
    }
    if (cfg.tlsSkipVerify && cfg.serverUrl.startsWith("https") && !this.insecureAgent) {
      this.insecureAgent = new HttpsAgent({ rejectUnauthorized: false });
    }
    return {
      baseUrl: cfg.serverUrl.replace(/\/+$/, ""),
      apiKey: cfg.apiKey || "",
      isHttps: cfg.serverUrl.startsWith("https")
    };
  }
  async get(path, query) {
    const { baseUrl } = this.getConfig();
    let url = `${baseUrl}${path}`;
    if (query) {
      const params = new URLSearchParams(query);
      url += `?${params.toString()}`;
    }
    return this.doRequest("GET", url);
  }
  async post(path, body) {
    const { baseUrl } = this.getConfig();
    return this.doRequest("POST", `${baseUrl}${path}`, body);
  }
  async patch(path, body) {
    const { baseUrl } = this.getConfig();
    return this.doRequest("PATCH", `${baseUrl}${path}`, body);
  }
  async delete(path) {
    const { baseUrl } = this.getConfig();
    return this.doRequest("DELETE", `${baseUrl}${path}`);
  }
  doRequest(method, url, body) {
    const { apiKey, isHttps } = this.getConfig();
    const parsed = new URL(url);
    const payload = body !== void 0 ? JSON.stringify(body) : void 0;
    const headers = {
      "x-api-key": apiKey
    };
    if (payload) {
      headers["Content-Type"] = "application/json";
      headers["Content-Length"] = Buffer.byteLength(payload).toString();
    }
    const requestFn = isHttps ? httpsRequest : httpRequest;
    return new Promise((resolve, reject) => {
      const req = requestFn(
        {
          hostname: parsed.hostname,
          port: parsed.port || (isHttps ? 443 : 80),
          path: parsed.pathname + parsed.search,
          method,
          headers,
          ...this.insecureAgent ? { agent: this.insecureAgent } : {}
        },
        (res) => {
          const chunks = [];
          res.on("data", (chunk) => chunks.push(chunk));
          res.on("end", () => {
            const text = Buffer.concat(chunks).toString();
            let json;
            try {
              json = JSON.parse(text);
            } catch {
              reject(new UnraidApiError(`Invalid JSON response: ${text.slice(0, 200)}`, res.statusCode ?? 0, "PARSE_ERROR"));
              return;
            }
            if (!json.ok) {
              reject(new UnraidApiError(json.error.message, res.statusCode ?? 0, json.error.code));
              return;
            }
            resolve(json.data);
          });
        }
      );
      req.on("error", (err) => {
        reject(new UnraidApiError(
          `Connection failed: ${err.message}`,
          0,
          "CONNECTION_ERROR"
        ));
      });
      if (payload) req.write(payload);
      req.end();
    });
  }
};

// src/tools/util.ts
function textResult(data) {
  return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
}
function errorResult(err) {
  const message = err instanceof Error ? err.message : String(err);
  return { content: [{ type: "text", text: `Error: ${message}` }] };
}

// src/tools/health.ts
function registerHealthTools(api, getClient) {
  api.registerTool({
    name: "unraid_health_check",
    description: "Check the health status of the Unraid server connection, including API and GraphQL reachability.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/health"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/docker.ts
function registerDockerTools(api, getClient) {
  api.registerTool({
    name: "unraid_docker_list",
    description: "List all Docker containers on the Unraid server with their current state, image, and status.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/docker/containers"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_docker_inspect",
    description: "Get detailed information about a specific Docker container including ports, mounts, and network mode.",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Container ID or name" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["id"]
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get(`/api/docker/containers/${params.id}`));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_docker_logs",
    description: "Get logs from a specific Docker container.",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Container ID or name" },
        tail: { type: "number", description: "Number of lines from the end (default: 100)" },
        since: { type: "string", description: "Show logs since timestamp (e.g., 2024-01-01T00:00:00Z)" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["id"]
    },
    execute: async (_id, params) => {
      try {
        const query = {};
        if (params.tail) query.tail = String(params.tail);
        if (params.since) query.since = String(params.since);
        return textResult(await getClient(params.server).get(`/api/docker/containers/${params.id}/logs`, query));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  for (const [toolName, desc, action] of [
    ["unraid_docker_start", "Start a stopped Docker container.", "start"],
    ["unraid_docker_stop", "Stop a running Docker container.", "stop"],
    ["unraid_docker_restart", "Restart a Docker container.", "restart"],
    ["unraid_docker_pause", "Pause a running Docker container (freeze all processes).", "pause"],
    ["unraid_docker_unpause", "Unpause a paused Docker container.", "unpause"]
  ]) {
    api.registerTool({
      name: toolName,
      description: desc,
      parameters: {
        type: "object",
        properties: {
          id: { type: "string", description: "Container ID or name" },
          server: { type: "string", description: "Target server name (optional, uses default server)" }
        },
        required: ["id"]
      },
      execute: async (_id, params) => {
        try {
          return textResult(await getClient(params.server).post(`/api/docker/containers/${params.id}/${action}`));
        } catch (err) {
          return errorResult(err);
        }
      }
    });
  }
  api.registerTool({
    name: "unraid_docker_remove",
    description: "Remove a Docker container. Pass force=true to stop and remove in one step. This is a destructive operation that cannot be undone.",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Container ID or name" },
        force: { type: "boolean", description: "Stop the container before removing (default: false)" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["id"]
    },
    execute: async (_id, params) => {
      try {
        const query = params.force ? "?force=true" : "";
        return textResult(await getClient(params.server).delete(`/api/docker/containers/${params.id}${query}`));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_docker_create",
    description: "Create and start a new Docker container on the Unraid server. Specify image, optional name, port mappings, volume mounts, environment variables, restart policy, and network.",
    parameters: {
      type: "object",
      properties: {
        image: { type: "string", description: "Docker image to use (e.g. vikunja/vikunja:latest)" },
        name: { type: "string", description: "Optional container name" },
        ports: {
          type: "array",
          items: { type: "string" },
          description: "Port mappings in host:container format (e.g. ['3456:3456'])"
        },
        volumes: {
          type: "array",
          items: { type: "string" },
          description: "Volume mounts in host:container format (e.g. ['/mnt/cache/appdata/vikunja:/app/vikunja'])"
        },
        env: {
          type: "array",
          items: { type: "string" },
          description: "Environment variables in KEY=VALUE format"
        },
        restart: {
          type: "string",
          enum: ["no", "always", "unless-stopped", "on-failure"],
          description: "Restart policy (default: unless-stopped)"
        },
        network: { type: "string", description: "Network to attach the container to" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["image"]
    },
    execute: async (_id, params) => {
      try {
        const { server, ...body } = params;
        return textResult(await getClient(server).post("/api/docker/containers", body));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/vms.ts
function registerVMTools(api, getClient) {
  api.registerTool({
    name: "unraid_vm_list",
    description: "List all virtual machines on the Unraid server with their current state.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/vms"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  for (const [name, desc, action] of [
    ["unraid_vm_inspect", "Get detailed information about a specific virtual machine.", null],
    ["unraid_vm_start", "Start a stopped virtual machine.", "start"],
    ["unraid_vm_stop", "Gracefully stop a running virtual machine (ACPI shutdown).", "stop"],
    ["unraid_vm_pause", "Pause a running virtual machine (suspend to RAM).", "pause"],
    ["unraid_vm_resume", "Resume a paused virtual machine.", "resume"],
    ["unraid_vm_force_stop", "Force stop a virtual machine (equivalent to pulling the power plug). This is destructive and may cause data loss.", "force-stop"],
    ["unraid_vm_reboot", "Reboot a running virtual machine (ACPI reboot).", "reboot"]
  ]) {
    api.registerTool(
      {
        name,
        description: desc,
        parameters: {
          type: "object",
          properties: {
            id: { type: "string", description: "VM ID or name" },
            server: { type: "string", description: "Target server name (optional, uses default server)" }
          },
          required: ["id"]
        },
        execute: async (_id, params) => {
          try {
            const client = getClient(params.server);
            if (action) {
              return textResult(await client.post(`/api/vms/${params.id}/${action}`));
            }
            return textResult(await client.get(`/api/vms/${params.id}`));
          } catch (err) {
            return errorResult(err);
          }
        }
      },
      ...name === "unraid_vm_force_stop" ? [{ optional: true }] : []
    );
  }
}

// src/tools/array.ts
function registerArrayTools(api, getClient) {
  api.registerTool({
    name: "unraid_array_status",
    description: "Get the current status of the Unraid array including state, capacity, disks, and parities. Capacity is in kilobytes (KiB). Disk 'size' fields are in kilobytes (KiB).",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/array/status"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_array_start",
    description: "Start the Unraid array. This will mount all disks and start Docker/VMs if configured.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/array/start"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_array_stop",
    description: "Stop the Unraid array. This will stop all Docker containers and VMs, then unmount all disks.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/array/stop"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_parity_status",
    description: "Get the current parity check status (running, progress, speed, errors).",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/array/parity/status"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_parity_start",
    description: "Start a parity check. Defaults to non-correcting (read-only) for safety. Set correct=true for a correcting check.",
    parameters: {
      type: "object",
      properties: {
        correct: {
          type: "boolean",
          description: "If true, run a correcting parity check. Defaults to false (non-correcting)."
        },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/array/parity/start", { correct: params.correct ?? false }));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_parity_pause",
    description: "Pause a running parity check.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/array/parity/pause"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_parity_resume",
    description: "Resume a paused parity check.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/array/parity/resume"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_parity_cancel",
    description: "Cancel a running or paused parity check.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/array/parity/cancel"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/disks.ts
function registerDiskTools(api, getClient) {
  api.registerTool({
    name: "unraid_disk_list",
    description: "List all disks (data + parity) with name, size, used, free, usedPercent, temp, status, and fsType.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/disks"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_disk_details",
    description: "Get details for a specific disk: size, used, free, usedPercent, temp, status, and fsType.",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Disk ID (e.g., 'disk1', 'parity')" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["id"]
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get(`/api/disks/${params.id}`));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/shares.ts
function registerShareTools(api, getClient) {
  api.registerTool({
    name: "unraid_share_list",
    description: "List all user shares on the Unraid server with their settings and usage. The 'free' and 'size' fields are in kilobytes (KiB).",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/shares"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_share_details",
    description: "Get details for a specific user share by name. The 'free' and 'size' fields are in kilobytes (KiB).",
    parameters: {
      type: "object",
      properties: {
        name: { type: "string", description: "Share name" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["name"]
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get(`/api/shares/${params.name}`));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_share_update",
    description: "Update safe settings for a user share. Only affects metadata and future write behavior -- does not move existing data.",
    parameters: {
      type: "object",
      properties: {
        name: { type: "string", description: "Share name to update" },
        comment: { type: "string", description: "Share description/comment" },
        allocator: { type: "string", description: "Disk allocation method: highwater, fill, or most-free" },
        floor: { type: "string", description: "Minimum free space per disk (e.g. '0' or '50000')" },
        splitLevel: { type: "string", description: "Split level for distributing files across disks" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["name"]
    },
    execute: async (_id, params) => {
      try {
        const { name, server, ...updates } = params;
        return textResult(await getClient(server).patch(`/api/shares/${name}`, updates));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/system.ts
function registerSystemTools(api, getClient) {
  api.registerTool({
    name: "unraid_system_info",
    description: "Get system information: OS (platform, hostname, uptime), CPU (model, cores, threads), memory (total, used, free, percent), and CPU load averages (1m, 5m, 15m).",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/system/info"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_system_metrics",
    description: "Get live system metrics: memory (total, used, free bytes, percent) and CPU load averages (1m, 5m, 15m). Lightweight endpoint for polling.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/system/metrics"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_service_list",
    description: "List system services and their current state.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/system/services"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_system_reboot",
    description: "Reboot the Unraid server. This is a destructive operation that will interrupt all running services, VMs, and containers.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/system/reboot"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_system_shutdown",
    description: "Shut down the Unraid server. This is a destructive operation that will power off the server.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post("/api/system/shutdown"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/notifications.ts
function registerNotificationTools(api, getClient) {
  api.registerTool({
    name: "unraid_notification_list",
    description: "List all system notifications with their importance level and archive status.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/notifications"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_notification_create",
    description: "Create a new system notification.",
    parameters: {
      type: "object",
      properties: {
        title: { type: "string", description: "Notification title" },
        subject: { type: "string", description: "Notification subject" },
        description: { type: "string", description: "Notification body text" },
        importance: { type: "string", description: "Importance level: alert, warning, or normal" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["title", "subject", "description"]
    },
    execute: async (_id, params) => {
      try {
        const body = {
          title: params.title,
          subject: params.subject,
          description: params.description
        };
        if (params.importance) body.importance = params.importance;
        return textResult(await getClient(params.server).post("/api/notifications", body));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_notification_archive",
    description: "Archive a notification (mark as read/handled).",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Notification ID" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["id"]
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).post(`/api/notifications/${params.id}/archive`));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
  api.registerTool({
    name: "unraid_notification_delete",
    description: "Delete a notification permanently.",
    parameters: {
      type: "object",
      properties: {
        id: { type: "string", description: "Notification ID" },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      },
      required: ["id"]
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).delete(`/api/notifications/${params.id}`));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/network.ts
function registerNetworkTools(api, getClient) {
  api.registerTool({
    name: "unraid_network_info",
    description: "Get network information including hostname, gateway, DNS servers, and all network interfaces.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/network"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/users.ts
function registerUserTools(api, getClient) {
  api.registerTool({
    name: "unraid_user_me",
    description: "Get information about the current authenticated user.",
    parameters: {
      type: "object",
      properties: {
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        return textResult(await getClient(params.server).get("/api/users/me"));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/tools/logs.ts
function registerLogTools(api, getClient) {
  api.registerTool({
    name: "unraid_syslog",
    description: "Get recent syslog entries from the Unraid server. Returns the most recent log lines.",
    parameters: {
      type: "object",
      properties: {
        lines: {
          type: "number",
          description: "Number of log lines to retrieve (1-1000, default 50)."
        },
        server: { type: "string", description: "Target server name (optional, uses default server)" }
      }
    },
    execute: async (_id, params) => {
      try {
        const query = {};
        if (params.lines) query.lines = String(params.lines);
        return textResult(await getClient(params.server).get("/api/logs/syslog", query));
      } catch (err) {
        return errorResult(err);
      }
    }
  });
}

// src/index.ts
function resolveServers(api) {
  const raw = api.config?.servers ?? api.pluginConfig?.servers ?? api.config?.plugins?.entries?.unraidclaw?.config?.servers;
  if (Array.isArray(raw) && raw.length > 0) return raw;
  const single = api.config?.serverUrl ? api.config : api.pluginConfig?.serverUrl ? api.pluginConfig : api.config?.plugins?.entries?.unraidclaw?.config;
  if (single?.serverUrl) {
    return [{ name: "default", serverUrl: single.serverUrl, apiKey: single.apiKey, tlsSkipVerify: single.tlsSkipVerify, default: true }];
  }
  return [];
}
function register(api) {
  const log = api.logger || console;
  const clients = /* @__PURE__ */ new Map();
  function getClient(serverName) {
    const servers2 = resolveServers(api);
    if (servers2.length === 0) {
      return new UnraidClient(() => ({ serverUrl: "", apiKey: "" }));
    }
    const target = serverName ? servers2.find((s) => s.name === serverName) : servers2.find((s) => s.default) ?? servers2[0];
    if (!target) {
      throw new Error(`Server "${serverName}" not found. Available: ${servers2.map((s) => s.name).join(", ")}`);
    }
    let client = clients.get(target.name);
    if (!client) {
      client = new UnraidClient(() => ({ serverUrl: target.serverUrl, apiKey: target.apiKey, tlsSkipVerify: target.tlsSkipVerify }));
      clients.set(target.name, client);
    }
    return client;
  }
  registerHealthTools(api, getClient);
  registerDockerTools(api, getClient);
  registerVMTools(api, getClient);
  registerArrayTools(api, getClient);
  registerDiskTools(api, getClient);
  registerShareTools(api, getClient);
  registerSystemTools(api, getClient);
  registerNotificationTools(api, getClient);
  registerNetworkTools(api, getClient);
  registerUserTools(api, getClient);
  registerLogTools(api, getClient);
  const servers = resolveServers(api);
  if (servers.length > 1) {
    log.info(`UnraidClaw: registered tools for ${servers.length} servers: ${servers.map((s) => s.name).join(", ")}`);
  } else if (servers.length === 1) {
    log.info(`UnraidClaw: registered tools, server: ${servers[0].serverUrl}`);
  } else {
    log.info(`UnraidClaw: registered tools (config will resolve at runtime)`);
  }
}
export {
  register as default
};
