const express = require("express");
const cors = require("cors");
const multer = require("multer");
const {
  getAuditTimeline,
  getControlSummary,
  getQueueStatus,
  getRuntimeHealth,
  getRuntimeStatus,
  getVisibilitySnapshot
} = require("./runtimeApiService");

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors());
app.use(express.json());

// Quick check endpoint
app.get("/api/health", (req, res) => {
  res.json({ ok: true, service: "orchestrator", ts: Date.now() });
});

app.get("/api/runtime/status", (req, res) => {
  res.json(getRuntimeStatus());
});

app.get("/api/runtime/queue", (req, res) => {
  res.json(getQueueStatus());
});

app.get("/api/runtime/audit", (req, res) => {
  res.json(getAuditTimeline({ recent: req.query.recent }));
});

app.get("/api/runtime/health", (req, res) => {
  res.json(getRuntimeHealth({ staleHeartbeatMinutes: req.query.staleHeartbeatMinutes }));
});

app.get("/api/runtime/visibility", (req, res) => {
  res.json(getVisibilitySnapshot());
});

app.get("/api/runtime/control", (req, res) => {
  res.json(getControlSummary());
});

// Pipeline endpoint (accepts 2 uploads)
app.post(
  "/api/pipeline/run",
  upload.fields([
    { name: "whitepaper", maxCount: 1 },
    { name: "readme", maxCount: 1 },
  ]),
  (req, res) => {
    const wp = req.files?.whitepaper?.[0];
    const rm = req.files?.readme?.[0];

    if (!wp || !rm) {
      return res.status(400).json({
        ok: false,
        error: "Missing required uploads: whitepaper + readme",
      });
    }

    // Planned pipeline stages only; this endpoint does not execute them yet.
    const stages = [
      { key: "validate", label: "Validate inputs", status: "PLANNED_NOT_EXECUTED" },
      { key: "parse", label: "Parse intent & constraints", status: "PLANNED_NOT_EXECUTED" },
      { key: "classify", label: "Classify project type", status: "PLANNED_NOT_EXECUTED" },
      { key: "scaffold", label: "Generate scaffold", status: "PLANNED_NOT_EXECUTED" },
      { key: "done", label: "Done", status: "PLANNED_NOT_EXECUTED" },
    ];

    return res.json({
      ok: true,
      status: "STUB",
      received: {
        whitepaper: { name: wp.originalname, size: wp.size, type: wp.mimetype },
        readme: { name: rm.originalname, size: rm.size, type: rm.mimetype },
      },
      stages,
      message:
        "Pipeline run endpoint accepts inputs, but it is currently a stub and does not execute pipeline stages yet.",
    });
  }
);

const PORT = 5050;
app.listen(PORT, () => {
  console.log(`[orchestrator] listening on http://localhost:${PORT}`);
});
