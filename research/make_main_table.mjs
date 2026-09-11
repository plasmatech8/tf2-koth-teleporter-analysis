import fs from "node:fs";

const model = JSON.parse(fs.readFileSync(new URL("./report_model.json", import.meta.url), "utf8"));

const one = value => Number(value).toFixed(1);
const signed = value => `${value >= 0 ? "+" : ""}${one(value)}`;

function timeline(alternative) {
  const merged = [];
  for (const interval of alternative.net.intervals) {
    const previous = merged.at(-1);
    if (previous?.margin === interval.margin) previous.duration += interval.duration;
    else merged.push({ duration: interval.duration, margin: interval.margin });
  }
  const parts = merged.map(interval => {
    if (interval.margin === 0) return `**${one(interval.duration)} s even**`;
    return `**${one(interval.duration)} s of ${interval.margin > 0 ? "+" : ""}${interval.margin}**`;
  });
  parts.push(`*(${signed(alternative.net.playerSeconds)} p·s)*`);
  return parts.join("<br>");
}

function makeTable(mapId) {
  const rows = model.scenarios.filter(item => item.map === mapId);
  const output = [
    "| Case | Attack spawn offsets | Defence spawn offsets | No tele | **Rebuild L1** | Rebuild L2 | **Keep L3** | **Extra from keeping L3 (vs L1)** |",
    "|---:|---|---|---|---|---|---|---:|",
  ];
  for (const row of rows) {
    const attack = row.attack.join(", ");
    const defence = row.defence.map(item => item.spawn).join(", ");
    const delta = signed(row.alternatives.l3_vs_l1.playerSeconds);
    output.push(`| **${row.id}** | \`${attack}\` | \`${defence}\` | ${timeline(row.alternatives.walk)} | ${timeline(row.alternatives.l1)} | ${timeline(row.alternatives.l2)} | ${timeline(row.alternatives.l3)} | **${delta} p·s** |`);
  }
  return output.join("\n");
}

const mapIndex = process.argv.indexOf("--map");
const mapId = mapIndex >= 0 ? process.argv[mapIndex + 1] : "product";
console.log(makeTable(mapId));
