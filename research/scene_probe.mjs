import fs from 'node:fs';
import readline from 'node:readline';

const [id, tickText, userText, radiusText] = process.argv.slice(2);
if (!id || !tickText || !userText) throw new Error('usage: node scene_probe.mjs <demo-id> <tick> <user-id>');
const olders = [];
const newers = [];
const events = [];
const target = Number(tickText);
const radius = radiusText ? Number(radiusText) : 1200;
const allUsers = userText === 'all';
const user = allUsers ? null : Number(userText);
const input = `research/history/${id}.json.jsonl`;
for await (const line of readline.createInterface({input: fs.createReadStream(input), crlfDelay: Infinity})) {
  const value = JSON.parse(line);
  if (value.kind === 'snapshot' && Math.abs((value.tick ?? 0) - target) <= 300) {
    const player = allUsers ? null : value.players.find(item => item.user === user);
    if (player) {
      const row = {tick: value.tick, player};
      if (value.tick <= target) olders.push(row);
      else newers.push(row);
    }
  }
  if (value.kind === 'event' && Math.abs((value.tick ?? 0) - target) <= radius) {
    const data = value.data ?? {};
    const relevantAll = allUsers && ['player_spawn', 'player_death', 'player_teleported', 'teamplay_point_captured', 'teamplay_round_win'].includes(value.name);
    if (relevantAll || data.user_id === user || data.attacker === user || data.healer === user || data.patient === user) {
      events.push({tick: value.tick, name: value.name, data});
    }
  }
}
console.log(JSON.stringify({before: olders.slice(-3), after: newers.slice(0, 8), events}, null, 2));
