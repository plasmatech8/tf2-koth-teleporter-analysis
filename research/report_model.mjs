import fs from 'node:fs';

const maps = {
  product: { label: 'Product', entrance: 2, exitToFront: 4, walk: 12 },
  ashville: { label: 'Ashville', entrance: 2, exitToFront: 3, walk: 12 },
};
const transit = 0.6;
const cycles = { l1: 10.6, l2: 5.6, l3: 3.6 };
// Team preference: riders do not wait more than one second at any tele level.
const maxQueueWait = { l1: 1, l2: 1, l3: 1 };

const scenarios = [
  { id: '1A', trades: 1, attack: [0], defence: [4], phase: '4-second difference' },
  { id: '1B', trades: 1, attack: [0], defence: [8], phase: '8-second difference' },
  { id: '2A', trades: 2, attack: [0, 4], defence: [8, 8], phase: 'first pair: 8-second difference' },
  { id: '2B', trades: 2, attack: [0, 4], defence: [4, 12], phase: 'first pair: 4-second difference' },
  { id: '3A', trades: 3, attack: [0, 4, 8], defence: [8, 8, 16], phase: 'first pair: 8-second difference' },
  { id: '3B', trades: 3, attack: [0, 4, 8], defence: [4, 12, 12], phase: 'first pair: 4-second difference' },
  { id: '4A', trades: 4, attack: [0, 4, 8, 12], defence: [8, 8, 16, 16], phase: 'first pair: 8-second difference' },
  { id: '4B', trades: 4, attack: [0, 4, 8, 12], defence: [4, 12, 12, 20], phase: 'first pair: 4-second difference' },
];

function arrivals(spawns, map, infrastructure) {
  if (infrastructure === 'walk') return spawns.map((spawn, i) => ({ player: i + 1, spawn, arrival: spawn + map.walk, mode: 'walk' }));
  let ready = -Infinity;
  return spawns.map((spawn, i) => {
    const entranceArrival = spawn + map.entrance;
    const use = Math.max(entranceArrival, ready);
    const queueWait = use - entranceArrival;
    const teleArrival = use + transit + map.exitToFront;
    const walkArrival = spawn + map.walk;
    const waitLimit = maxQueueWait[infrastructure];
    if ((waitLimit === null || queueWait <= waitLimit) && teleArrival < walkArrival) {
      ready = use + cycles[infrastructure];
      return { player: i + 1, spawn, arrival: teleArrival, mode: infrastructure, entranceArrival, use, queueWait };
    }
    return { player: i + 1, spawn, arrival: walkArrival, mode: 'walk', entranceArrival, rejectedQueueWait: queueWait };
  });
}

function timeline(positiveArrivals, negativeArrivals) {
  const changes = new Map();
  for (const x of positiveArrivals) changes.set(x.arrival, (changes.get(x.arrival) ?? 0) + 1);
  for (const x of negativeArrivals) changes.set(x.arrival, (changes.get(x.arrival) ?? 0) - 1);
  const times = [...changes.keys()].sort((a, b) => a - b);
  let margin = 0;
  const intervals = [];
  for (let i = 0; i < times.length; i++) {
    const start = times[i];
    margin += changes.get(start);
    const end = times[i + 1];
    if (end !== undefined && end > start) intervals.push({ start, end, duration: end - start, margin });
  }
  const durations = {};
  for (const x of intervals) durations[x.margin] = (durations[x.margin] ?? 0) + x.duration;
  return {
    intervals,
    durations,
    playerSeconds: intervals.reduce((sum, x) => sum + x.margin * x.duration, 0),
    maxAdvantage: Math.max(0, ...intervals.map(x => x.margin)),
    maxDisadvantage: Math.min(0, ...intervals.map(x => x.margin)),
    timeAtLeastPlus2: intervals.filter(x => x.margin >= 2).reduce((sum, x) => sum + x.duration, 0),
  };
}

const output = { inputs: { maps, transit, cycles, maxQueueWait }, scenarios: [] };
for (const [mapId, map] of Object.entries(maps)) {
  for (const scenario of scenarios) {
    const defence = arrivals(scenario.defence, map, 'l3');
    const alternatives = {};
    for (const infrastructure of ['l3', 'walk', 'l1', 'l2']) {
      const attack = arrivals(scenario.attack, map, infrastructure);
      alternatives[infrastructure] = { attack, net: timeline(attack, defence) };
    }
    alternatives.l3_vs_l1 = timeline(alternatives.l3.attack, alternatives.l1.attack);
    alternatives.l3_vs_walk = timeline(alternatives.l3.attack, alternatives.walk.attack);
    alternatives.l3_vs_l2 = timeline(alternatives.l3.attack, alternatives.l2.attack);
    output.scenarios.push({ map: mapId, ...scenario, defence, alternatives });
  }
}

fs.writeFileSync('research/report_model.json', JSON.stringify(output, null, 2));
console.log('wrote research/report_model.json');
