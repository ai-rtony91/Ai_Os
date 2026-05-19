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

    // The pipeline stages (muscle wiring starts here)
    const stages = [
      { key: "validate", label: "Validate inputs" },
      { key: "parse", label: "Parse intent & constraints" },
      { key: "classify", label: "Classify project type" },
      { key: "scaffold", label: "Generate scaffold" },
      { key: "done", label: "Done" },
    ];

    // For now: return metadata + stages (real API plumbing)
    return res.json({
      ok: true,
      received: {
        whitepaper: { name: wp.originalname, size: wp.size, type: wp.mimetype },
        readme: { name: rm.originalname, size: rm.size, type: rm.mimetype },
      },
      stages,
      message: "Pipeline wired. Next step will run these stages progressively.",
    });
  }
);

const PORT = 5050;
app.listen(PORT, () => {
  console.log(`[orchestrator] listening on http://localhost:${PORT}`);
});
