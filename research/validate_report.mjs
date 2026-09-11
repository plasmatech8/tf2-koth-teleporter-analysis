import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const root = path.resolve(import.meta.dirname, "..");
const reportPath = path.join(root, "TF2_KOTH_Teleporter_Report.md");
const report = fs.readFileSync(reportPath, "utf8").replace(/\r\n/g, "\n");
const model = JSON.parse(fs.readFileSync(path.join(root, "research", "report_model.json"), "utf8"));
const audit = JSON.parse(fs.readFileSync(path.join(root, "research", "respawn_pair_audit.json"), "utf8"));
const figureSource = fs.readFileSync(path.join(root, "research", "report_figures.py"), "utf8");

const errors = [];
const assert = (condition, message) => {
  if (!condition) errors.push(message);
};

// Every local Markdown link and image must resolve from the report directory.
for (const match of report.matchAll(/!?\[[^\]]*\]\(([^)]+)\)/g)) {
  const target = match[1].split("#", 1)[0];
  if (/^(?:https?:|mailto:)/.test(target)) continue;
  assert(fs.existsSync(path.resolve(root, target)), `Missing local target: ${target}`);
}

// Markdown tables should use a consistent number of columns within each block.
const lines = report.split(/\r?\n/);
for (let index = 0; index < lines.length;) {
  if (!lines[index].startsWith("|")) {
    index += 1;
    continue;
  }
  const start = index;
  const counts = [];
  while (index < lines.length && lines[index].startsWith("|")) {
    counts.push((lines[index].match(/\|/g) ?? []).length);
    index += 1;
  }
  assert(new Set(counts).size === 1, `Inconsistent table columns near line ${start + 1}: ${counts.join(", ")}`);
}

// Check both generated detailed map tables.
const generatedProductTable = execFileSync(process.execPath, [path.join(root, "research", "make_main_table.mjs")], { encoding: "utf8" }).replace(/\r\n/g, "\n").trim();
assert(report.includes(generatedProductTable), "The detailed Product comparison table is missing or stale");
const generatedAshvilleTable = execFileSync(process.execPath, [path.join(root, "research", "make_main_table.mjs"), "--map", "ashville"], { encoding: "utf8" }).replace(/\r\n/g, "\n").trim();
assert(report.includes(generatedAshvilleTable), "The detailed Ashville comparison table is missing or stale");

const finalAudit = audit.summary.productAndAshvilleFinal1;
assert(report.includes(`${finalAudit.simultaneousPairs} near-simultaneous opposing death pairs`), "Respawn pair count is stale");
assert(report.includes(`${finalAudit.fourSecondSpawnGap} four-second gaps (58.3%) and ${finalAudit.eightSecondSpawnGap} eight-second gaps (41.7%)`), "Respawn gap counts are stale");
assert(report.includes("giving a theoretical 50% chance of +2 when two players per team trade lives"), "Two-player alignment probability wording is missing");
assert(report.includes("produces at least four seconds at +2 in five"), "Multi-player threshold wording is missing");
assert(report.includes("both alignments with three or four returning players"), "Multi-player alignment wording is missing");
assert(report.includes("With two returning attackers, keeping L3 gives a clear advantage over rebuilt L1"), "Two-return direct comparison wording is missing");
assert(report.includes("one attacker returns on each successive four-second attacking wave"), "One-at-a-time attacking return wording is missing");
assert(report.includes("21.1 - 10.4 - 2.0") && report.includes("21.1 - 12.4 - 2.0"), "Entrance-based rebuild-readiness arithmetic is missing");
assert(report.includes("about 299 HU/s") && !report.includes("Sniper and Spy"), "Current class-speed wording is missing or stale");
assert(report.includes("11 h 46.5 min") && report.includes("4 h 20.8 min") && report.includes("16 h 7.3 min"), "Exact displayed active-play totals are missing");
assert(figureSource.includes("both defenders respawn together") && figureSource.includes("two pairs respawn together"), "Respawn-together chart labels are missing");
assert(figureSource.includes("tmax = 20"), "The two-player chart does not include its 20-second arrivals within the formal axis range");
for (const image of [
  "step-1-average-trade-timeline.png",
  "step-2-wave-alignments-timeline.png",
  "step-3-no-tele-timeline.png",
  "step-4-rebuild-readiness-timeline.png",
  "step-5-shared-tele-timeline.png",
]) {
  assert(report.includes(image), `Missing calculation explainer figure: ${image}`);
}
assert(report.includes("A player dies late or respawns behind the group"), "Late or staggered respawn factor is missing");
assert(report.includes("Favours keeping the exit") && report.includes("Favours destroying the exit") && report.includes("Changes how much either choice matters"), "Directional decision-factor groups are missing");
assert(model.inputs.maxQueueWait.l1 === 1 && model.inputs.maxQueueWait.l2 === 1 && model.inputs.maxQueueWait.l3 === 1, "The one-second all-level wait rule is missing from the model");
for (const [map, trades, expected] of [["product", 2, 5.4], ["product", 4, 10.8], ["ashville", 2, 6.4], ["ashville", 4, 12.8]]) {
  const row = model.scenarios.find(x => x.map === map && x.trades === trades);
  assert(Math.abs(row.alternatives.l3_vs_l1.playerSeconds - expected) < 1e-6, `Unexpected ${map} ${trades}-return L3-L1 total`);
  assert(report.includes(`**+${expected.toFixed(1)} p·s**`), `Missing ${map} ${trades}-return headline total`);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log("Report validation passed: model tables, one-second wait rule, respawn audit, headline totals, threshold wording, and local links are consistent.");
}
