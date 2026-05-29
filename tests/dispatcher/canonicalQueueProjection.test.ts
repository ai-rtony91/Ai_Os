import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import {
  buildCanonicalQueueProjection,
  normalizePacketState
} from "../../services/dispatcher/canonicalQueueProjection.ts";

function writePacket(root: string, name: string, packet: object): void {
  writeFileSync(join(root, name), JSON.stringify(packet, null, 2), "utf8");
}

test("normalizes known packet states", () => {
  assert.equal(normalizePacketState("active"), "queued");
  assert.equal(normalizePacketState("awaiting approval"), "approval_pending");
  assert.equal(normalizePacketState("dry_run_done"), "validated");
  assert.equal(normalizePacketState("DONE"), "completed");
});

test("projects ready packets without mutating source files", () => {
  const root = mkdtempSync(join(tmpdir(), "aios-queue-ready-"));
  const packetPath = join(root, "ready.json");
  const packet = {
    packet_id: "PKT-READY",
    title: "Ready packet",
    status: "active",
    risk_level: "low",
    allowed_paths: ["docs/reports/"],
    forbidden_paths: ["secrets/"]
  };

  writePacket(root, "ready.json", packet);
  const before = readFileSync(packetPath, "utf8");
  const projection = buildCanonicalQueueProjection({
    packetRoot: root,
    now: new Date("2026-05-29T00:00:00.000Z")
  });
  const after = readFileSync(packetPath, "utf8");

  assert.equal(projection.schema, "AIOS_CANONICAL_QUEUE_PROJECTION.v1");
  assert.equal(projection.projection_mode, "read_only");
  assert.equal(projection.packets[0]?.state, "ready");
  assert.equal(projection.packets[0]?.scheduler_eligible, true);
  assert.equal(projection.summary.ready, 1);
  assert.equal(after, before);
});

test("projects blocked packets", () => {
  const root = mkdtempSync(join(tmpdir(), "aios-queue-blocked-"));
  writePacket(root, "blocked.json", {
    packet_id: "PKT-BLOCKED",
    title: "Blocked packet",
    status: "active",
    risk_level: "medium",
    blockers: ["approval missing"]
  });

  const projection = buildCanonicalQueueProjection({ packetRoot: root });

  assert.equal(projection.packets[0]?.state, "blocked");
  assert.equal(projection.packets[0]?.scheduler_eligible, false);
  assert.equal(projection.summary.blocked, 1);
});

test("handles malformed packet JSON with warnings", () => {
  const root = mkdtempSync(join(tmpdir(), "aios-queue-malformed-"));
  writeFileSync(join(root, "bad.json"), "{", "utf8");

  const projection = buildCanonicalQueueProjection({ packetRoot: root });

  assert.equal(projection.packets.length, 0);
  assert.equal(projection.warnings.length, 1);
  assert.match(projection.warnings[0] ?? "", /malformed JSON skipped/);
});

test("projects unknown states for manual review", () => {
  const root = mkdtempSync(join(tmpdir(), "aios-queue-unknown-"));
  writePacket(root, "unknown.json", {
    packet_id: "PKT-UNKNOWN",
    title: "Unknown packet",
    status: "mystery",
    risk_level: "low"
  });

  const projection = buildCanonicalQueueProjection({ packetRoot: root });

  assert.equal(projection.packets[0]?.state, "unknown");
  assert.equal(projection.packets[0]?.scheduler_eligible, false);
  assert.equal(projection.summary.unknown, 1);
});
