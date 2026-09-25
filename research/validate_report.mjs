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

const finalAudit = audit.summary.allMapVersions;
assert(report.includes(`${finalAudit.simultaneousPairs} near-simultaneous opposing death pairs`), "Respawn pair count is stale");
assert(report.includes(`four seconds for ${finalAudit.fourSecondWaveAlignment} pairs (58.9%) and eight seconds for ${finalAudit.eightSecondWaveAlignment} (41.1%)`), "Respawn alignment counts are stale");
assert(finalAudit.otherWaveAlignment === 0, "Every audited pair must classify as a four- or eight-second wave alignment");
assert(finalAudit.observedSpawnGap.other === 1, "The documented delayed attacking spawn must remain visible in the raw event-gap count");
assert(report.includes("3.105 seconds apart") && report.includes("spawned about 0.9 seconds after the four-second wave"), "The delayed attacking spawn explanation is missing");
assert(report.includes("giving a theoretical 50% chance of +2 when two players per team trade lives"), "Two-player alignment probability wording is missing");
assert(report.includes("produces at least four seconds at +2 in five"), "Multi-player threshold wording is missing");
assert(report.includes("both alignments with three or four returning players"), "Multi-player alignment wording is missing");
assert(report.includes("With two returning attackers, keeping L3 gives a clear advantage over rebuilt L1"), "Two-return direct comparison wording is missing");
assert(report.includes("one attacker returns on each successive four-second attacking wave"), "One-at-a-time attacking return wording is missing");
assert(
  report.includes("21.1 s construction - 10.4 s death-to-spawn - 2.0 s spawn-to-entrance") &&
    report.includes("21.1 s construction - 12.4 s death-to-spawn - 2.0 s spawn-to-entrance"),
  "Entrance-based rebuild-readiness arithmetic is missing",
);
assert(report.includes("The 7-9 second figure is a **minimum delay**, not a window"), "Placement-zero chart explanation is missing");
assert(figureSource.includes("The 7-9 second staging rule: minimum time before the next relevant death") && figureSource.includes("Too-early example"), "Placement-zero rebuild chart is missing");
assert(report.includes("Teleporter transfer sequence") && report.includes("READY -> SENDING -> RECEIVING -> RECEIVING_RELEASE -> RECHARGING -> READY"), "Transfer-sequence appendix note is missing");
assert(report.includes("Appendix: expanded Product scenario timelines"), "Expanded scenario appendix is missing");
assert(report.includes("Product scenario 4A - four-second defender alignment"), "Expanded 4A alignment heading is missing");
assert(report.includes("Product scenario 4B - eight-second defender alignment"), "Expanded 4B alignment heading is missing");
assert(report.includes("product-scenario-4a-shared-tele-with-no-tele.png") && report.includes("product-scenario-4b-shared-tele-with-no-tele.png"), "Expanded scenario appendix figures are missing");
assert(report.includes("Sensitivity: attacking returns eight seconds apart"), "Eight-second attacking-return sensitivity is missing");
assert(report.includes("product-eight-second-return-spacing-a.png") && report.includes("product-eight-second-return-spacing-b.png"), "Eight-second attacking-return sensitivity figures are missing");
assert(report.includes("L2 recharges in time to serve every rider and therefore matches L3"), "Eight-second attacking-return sensitivity conclusion is missing");
assert(figureSource.includes("attacker_spawns_8s = [0.0, 8.0, 16.0, 24.0]"), "Eight-second attacking-return figure inputs are missing");
assert(figureSource.includes("eight-second defender alignment") && figureSource.includes("four-second defender alignment"), "Expanded scenario chart alignment labels are missing");
for (const map of ["product", "ashville"]) {
  for (const trades of [1, 2, 3, 4]) {
    const a = model.scenarios.find(x => x.map === map && x.id === `${trades}A`);
    const b = model.scenarios.find(x => x.map === map && x.id === `${trades}B`);
    assert(a?.defence[0]?.spawn === 4, `${map} ${trades}A must use the less favourable four-second first-defender gap`);
    assert(b?.defence[0]?.spawn === 8, `${map} ${trades}B must use the eight-second first-defender gap`);
  }
}
assert(report.includes("A means the defender's first return is four seconds behind; B means it is eight seconds behind"), "Main-table A/B convention is missing");
assert(report.includes("retained L3 could have brought Sniper back about 6.4 seconds earlier"), "Sniper return-time wording is missing");
assert(report.includes("crossed the audit's front-line threshold sooner than the generic rollout model predicted"), "Position-threshold wording is missing");
assert(report.includes("allow an additional return during a long fight"), "Long-fight return wording is missing");
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
assert(report.includes("A Level 3 teleporter has 216 health, compared with 150 at Level 1"), "Retained-L3 durability factor is missing");
assert(report.includes("The live game state may not fit one clean label") && report.includes("staging can overlap active combat"), "Ambiguous live-state qualifier is missing");
assert(report.includes("Favours keeping the exit") && report.includes("Favours destroying the exit") && report.includes("Changes how much either choice matters"), "Directional decision-factor groups are missing");
assert(report.includes("Across 46 recordings covering 114 rounds") && report.includes("44 reset-like uses, of which 7 were followed by death within 5 seconds"), "Unsafe-use count summary is missing");
assert(report.includes("2 clear harmful known-reset uses") && report.includes("1 additional unsafe known-reset use where the player survived"), "Unsafe-use review classifications are missing");
assert(figureSource.includes("if item['mode'] != 'walk' and 'entranceArrival' in item") && figureSource.includes("f\"{item['arrival']:.1f}s ({mode})\""), "Scenario 2B defender route markers are ambiguous");
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
