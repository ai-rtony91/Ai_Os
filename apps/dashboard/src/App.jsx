import { useMemo, useState } from "react";
import "./App.css";

const steps = [
  { key: "upload", title: "Upload Inputs" },
  { key: "review", title: "Review & Confirm" },
  { key: "generate", title: "Generate Project" },
  { key: "done", title: "Done" },
];

export default function App() {
  const [stepIndex, setStepIndex] = useState(0);
  const step = steps[stepIndex];

  const [whitePaper, setWhitePaper] = useState(null);
  const [readme, setReadme] = useState(null);

  // Step gating:
  // - upload: Next disabled until both files selected
  // - review: Next enabled
  // - generate: Next disabled (generation happens via the button)
  const canNext = useMemo(() => {
    if (step.key === "upload") return !!whitePaper && !!readme;
    if (step.key === "review") return true;
    return false;
  }, [step.key, whitePaper, readme]);

  const next = () => setStepIndex((i) => Math.min(i + 1, steps.length - 1));
  const back = () => setStepIndex((i) => Math.max(i - 1, 0));

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">AI‑OS</div>

        <div className="stepper">
          {steps.map((s, i) => (
            <div
              key={s.key}
              className={`step ${i === stepIndex ? "active" : i < stepIndex ? "done" : ""}`}
            >
              <span className="dot">{i + 1}</span>
              <span className="label">{s.title}</span>
            </div>
          ))}
        </div>
      </header>

      <main className="card">
        <h1>{step.title}</h1>

        {/* STEP 1: Upload */}
        {step.key === "upload" && (
          <>
            <p className="muted">Upload both files to continue.</p>

            <div className="field">
              <label>White Paper (PDF/MD)</label>
              <input
                type="file"
                onChange={(e) => setWhitePaper(e.target.files?.[0] || null)}
              />
              <div className="hint">
                {whitePaper ? `Selected: ${whitePaper.name}` : "No file selected"}
              </div>
            </div>

            <div className="field">
              <label>README.md</label>
              <input
                type="file"
                onChange={(e) => setReadme(e.target.files?.[0] || null)}
              />
              <div className="hint">
                {readme ? `Selected: ${readme.name}` : "No file selected"}
              </div>
            </div>
          </>
        )}

        {/* STEP 2: Review */}
        {step.key === "review" && (
          <>
            <p className="muted">Confirm what you uploaded, then click Next.</p>
            <div className="summary">
              <div><b>White Paper:</b> {whitePaper?.name || "—"}</div>
              <div><b>README:</b> {readme?.name || "—"}</div>
            </div>
          </>
        )}

        {/* STEP 3: Generate */}
        {step.key === "generate" && (
          <>
            <p className="muted">
              Generate runs only after Steps 1 & 2. Backend must be running on{" "}
              <b>http://localhost:5050</b>.
            </p>

            <button
              className="primary"
              disabled={!whitePaper || !readme}
              onClick={async () => {
                if (!whitePaper || !readme) return;

                try {
                  const form = new FormData();
                  form.append("whitepaper", whitePaper);
                  form.append("readme", readme);

                  const resp = await fetch("http://localhost:5050/api/pipeline/run", {
                    method: "POST",
                    body: form,
                  });

                  const data = await resp.json();

                  if (!data.ok) {
                    alert(data.error || "Pipeline failed");
                    return;
                  }

                  alert("✅ Pipeline stages: " + data.stages.map((s) => s.key).join(" → "));
                  next(); // advance to Done only after success
                } catch (e) {
                  alert("Backend not reachable. Is it running on http://localhost:5050 ?");
                }
              }}
            >
              Run Generation (Backend)
            </button>

            <p className="hint" style={{ marginTop: "10px" }}>
              If this button is disabled, go Back and upload both files.
            </p>
          </>
        )}

        {/* STEP 4: Done */}
        {step.key === "done" && (
          <>
            <h2>✅ Connected</h2>
            <p className="muted">
              UI → Backend pipeline wiring is working. Next we’ll replace alerts with on-screen progress.
            </p>
          </>
        )}

        {/* Navigation */}
        <div className="nav">
          <button onClick={back} disabled={stepIndex === 0}>
            Back
          </button>

          <button
            onClick={next}
            disabled={!canNext || step.key === "generate" || step.key === "done"}
          >
            Next
          </button>
        </div>
      </main>
    </div>
  );
}