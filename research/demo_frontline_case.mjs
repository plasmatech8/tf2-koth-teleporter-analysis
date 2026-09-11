import fs from 'node:fs';
import readline from 'node:readline';

const id = 1496366;
const threshold = 0.35;
const audit = JSON.parse(fs.readFileSync(`research/history/${id}.audit.json`, 'utf8'));
const scenarios = JSON.parse(fs.readFileSync('research/history/cost_scenarios.json', 'utf8'));
const scenario = scenarios.find(x => x.id === id && x.destruction === 1479.75 && x.threshold === 4 && x.maintained === true);
if (!scenario) throw new Error('Target scenario not found');

const windows = scenario.rides
  .filter(x => x.attack_saved > 0)
  .map(x => ({ ...x, start: x.tele_arrival, end: x.tele_arrival + x.attack_saved }));
const ownTeam = 'blue';
const enemyTeam = 'red';

const progress = (p, team) => {
  const a = audit.spawnCenters[team];
  const b = audit.spawnCenters[team === 'red' ? 'blue' : 'red'];
  return ((p.position.x - a.x) * (b.x - a.x) + (p.position.y - a.y) * (b.y - a.y)) /
    ((b.x - a.x) ** 2 + (b.y - a.y) ** 2);
};
const alive = p => p.state === 'Alive' && p.health > 0;
const front = (p, includeSpy) => alive(p) && p.in_pvs && p.class !== 'other' && (includeSpy || p.class !== 'spy') && progress(p, p.team) >= threshold;

const samples = [];
for await (const line of readline.createInterface({ input: fs.createReadStream(`research/history/${id}.json.jsonl`), crlfDelay: Infinity })) {
  const s = JSON.parse(line);
  if (s.kind !== 'snapshot') continue;
  const t = s.tick * 0.015;
  if (t < scenario.reopen || t > scenario.restored) continue;
  const count = (team, includeSpy) => s.players.filter(p => p.team === team && front(p, includeSpy)).length;
  const ownNonSpy = count(ownTeam, false);
  const enemyNonSpy = count(enemyTeam, false);
  const ownAll = count(ownTeam, true);
  const enemyAll = count(enemyTeam, true);
  const additions = windows.filter(w => t >= w.start && t < w.end && !s.players.some(p => p.user === w.user && front(p, false))).length;
  samples.push({
    t,
    actualNonSpy: ownNonSpy - enemyNonSpy,
    keepNonSpy: ownNonSpy + additions - enemyNonSpy,
    actualAll: ownAll - enemyAll,
    keepAll: ownAll + additions - enemyAll,
    additions,
  });
}

function summarise(field) {
  const duration = {};
  for (let i = 0; i < samples.length - 1; i++) {
    const dt = samples[i + 1].t - samples[i].t;
    const value = samples[i][field];
    duration[value] = (duration[value] ?? 0) + dt;
  }
  return Object.fromEntries(Object.entries(duration).sort((a, b) => Number(a[0]) - Number(b[0])).map(([k, v]) => [k, Number(v.toFixed(2))]));
}

const output = {
  definition: `alive and at least ${threshold} map-progress from own spawn; sampled about every 0.24 seconds`,
  window: { start: scenario.reopen, end: scenario.restored },
  earlierArrivalWindows: windows,
  durationByMargin: {
    actualNonSpy: summarise('actualNonSpy'),
    keepNonSpy: summarise('keepNonSpy'),
    actualAll: summarise('actualAll'),
    keepAll: summarise('keepAll'),
    teleCreated: summarise('additions'),
  },
  overlapSamples: samples.filter(x => x.additions >= 2),
};

fs.writeFileSync('research/demo_frontline_case.json', JSON.stringify(output, null, 2));
console.log(JSON.stringify(output.durationByMargin, null, 2));
