import fs from 'node:fs';
import readline from 'node:readline';
import assert from 'node:assert/strict';
let checks=[];
for(const file of fs.readdirSync('research/history').filter(x=>x.endsWith('.audit.json'))){
 const a=JSON.parse(fs.readFileSync('research/history/'+file));
 if(a.error)continue;
 const base=a.id===1502837?'research/product':`research/history/${a.id}`;
 const source=JSON.parse(fs.readFileSync(base+'.json'));
 let deaths=0,teleports=0,enemyUses=0;for await(const line of readline.createInterface({input:fs.createReadStream(base+'.json.jsonl'),crlfDelay:Infinity})){
  const e=JSON.parse(line);if(e.kind!=='event')continue;
  if(e.name==='player_death')deaths++;
  if(e.name==='player_teleported'&&a.ownIds.includes(e.data.builder_id)&&a.rounds.some(r=>r.start<=e.tick*.015&&e.tick*.015<r.end)){
   if(a.teleports.some(t=>t.tick===e.tick&&t.user===e.data.user_id))teleports++;
   else {assert.notEqual(source.state.summary.users[e.data.user_id]?.team,source.state.summary.users[e.data.builder_id]?.team,`unaccounted friendly teleport ${a.id}`);enemyUses++;}
  }
 }
 assert.equal(deaths,source.state.summary.deaths.length,`death event count ${a.id}`);
 assert.equal(teleports,a.teleports.length,`teleport count ${a.id}`);
 assert.ok(a.teleports.every(t=>!t.strict_candidate||t.broad_candidate));
 assert.ok(a.teleports.every(t=>t.death_s===null||t.death_s>=0));
 for(let i=1;i<a.rounds.length;i++)assert.ok(a.rounds[i].start>=a.rounds[i-1].end,`round overlap ${a.id}`);
 checks.push({id:a.id,deaths,teleports,enemyUses,rounds:a.rounds.length,passed:true});
}
fs.writeFileSync('research/history/verification.json',JSON.stringify(checks,null,2));console.log(checks.length,'parsed recordings verified');
