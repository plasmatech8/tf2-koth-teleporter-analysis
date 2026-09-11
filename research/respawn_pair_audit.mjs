import fs from 'node:fs';
import readline from 'node:readline';

const dir = 'research/history';
const dt = 0.015;
const manifest = JSON.parse(fs.readFileSync(`${dir}/manifest.json`, 'utf8'));
const rows = [];

const roundAt = (rounds, t) => rounds.find(r => r.start <= t && t < r.end);
const pausedBetween = (pauses, a, b) => pauses.some(p => p.start < b && p.end > a);

for (const item of manifest) {
  const auditPath = `${dir}/${item.id}.audit.json`;
  if (!fs.existsSync(auditPath)) continue;
  const audit = JSON.parse(fs.readFileSync(auditPath, 'utf8'));
  if (audit.error || !audit.rounds?.length) continue;

  const input = item.id === 1502837 ? 'research/product.json.jsonl' : `${dir}/${item.id}.json.jsonl`;
  if (!fs.existsSync(input)) continue;

  const events = [];
  for await (const line of readline.createInterface({ input: fs.createReadStream(input), crlfDelay: Infinity })) {
    const e = JSON.parse(line);
    if (e.kind === 'event' && ['player_death', 'player_spawn', 'teamplay_point_captured'].includes(e.name)) {
      events.push({ ...e, t: e.tick * dt });
    }
  }

  const caps = events.filter(e => e.name === 'teamplay_point_captured');
  const pending = new Map();
  const lives = [];

  for (const e of events) {
    const round = roundAt(audit.rounds, e.t);
    if (!round) continue;
    if (e.name === 'player_death') {
      pending.set(e.data.user_id, e);
      continue;
    }
    if (e.name !== 'player_spawn') continue;

    const death = pending.get(e.data.user_id);
    pending.delete(e.data.user_id);
    if (!death || death.t < round.start || pausedBetween(audit.pauses ?? [], death.t, e.t)) continue;

    const owner = caps.filter(c => c.t >= round.start && c.t <= death.t).at(-1)?.data.team;
    const changed = caps.some(c => c.t > death.t && c.t <= e.t);
    const delay = e.t - death.t;
    if (!owner || changed || e.data.class === 8 || delay < 6 || delay >= 30) continue;

    lives.push({
      id: item.id,
      map: audit.map,
      round: round.n,
      user: e.data.user_id,
      team: e.data.team,
      ownership: owner === e.data.team ? 'defence' : 'attack',
      deathTick: death.tick,
      death: death.t,
      spawnTick: e.tick,
      spawn: e.t,
      delay,
    });
  }

  const attackers = lives.filter(x => x.ownership === 'attack');
  const defenders = lives.filter(x => x.ownership === 'defence');
  for (const a of attackers) {
    for (const d of defenders) {
      if (a.round !== d.round || Math.abs(a.deathTick - d.deathTick) > 8) continue;
      rows.push({
        id: item.id,
        map: audit.map,
        round: a.round,
        attackDeathTick: a.deathTick,
        defenceDeathTick: d.deathTick,
        deathGap: Math.abs(a.death - d.death),
        attackDelay: a.delay,
        defenceDelay: d.delay,
        spawnGap: d.spawn - a.spawn,
      });
    }
  }
}

const near = (x, target, tolerance = 0.08) => Math.abs(x - target) <= tolerance;
const summarise = sample => ({
  simultaneousPairs: sample.length,
  fourSecondSpawnGap: sample.filter(x => near(x.spawnGap, 4)).length,
  eightSecondSpawnGap: sample.filter(x => near(x.spawnGap, 8)).length,
  otherSpawnGap: sample.filter(x => !near(x.spawnGap, 4) && !near(x.spawnGap, 8)).length,
  attackDelay: {
    min: Math.min(...sample.map(x => x.attackDelay)),
    max: Math.max(...sample.map(x => x.attackDelay)),
  },
  defenceDelay: {
    min: Math.min(...sample.map(x => x.defenceDelay)),
    max: Math.max(...sample.map(x => x.defenceDelay)),
  },
});

const summary = {
  allMapVersions: summarise(rows),
  productAndAshvilleFinal1: summarise(rows.filter(x => x.map !== 'koth_ashville_final2')),
};

fs.writeFileSync('research/respawn_pair_audit.json', JSON.stringify({ summary, rows }, null, 2));
console.log(JSON.stringify(summary, null, 2));
