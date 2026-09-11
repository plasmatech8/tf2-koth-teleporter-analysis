import fs from 'node:fs';
import readline from 'node:readline';
const dir='research/history', dt=.015;
const targetSteamId=process.env.TF2_ENGINEER_STEAM_ID;
if(!targetSteamId)throw new Error('Set TF2_ENGINEER_STEAM_ID to the Engineer Steam3 account ID used in the local demos.');
const rnd=x=>Number(x.toFixed(2)), med=a=>a.sort((a,b)=>a-b)[Math.floor(a.length/2)];
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y,a.z-b.z);
const alive=p=>p.state==='Alive'&&p.health>0;
const functional=x=>!x.tele.building&&!x.tele.sapped&&!x.extra?.m_bDisabled&&!x.extra?.m_bCarried&&!x.extra?.m_bPlacing&&[2,3,4,5,6].includes(x.extra?.m_iState);
const manifest=JSON.parse(fs.readFileSync(dir+'/manifest.json'));
for(const item of manifest){
 const base=`${dir}/${item.id}`;
 const input=item.id===1502837?'research/product':base;
 if(!fs.existsSync(input+'.json')||(fs.existsSync(base+'.audit.json')&&JSON.parse(fs.readFileSync(base+'.audit.json')).version>=4))continue;
 const source=JSON.parse(fs.readFileSync(input+'.json')); const users=source.state.summary.users;
 const pauses=(source.state.summary.pauses??[]).map(p=>({start:p.from*dt,end:p.to*dt}));
 const elapsed=(start,end)=>end-start-pauses.reduce((s,p)=>s+Math.max(0,Math.min(end,p.end)-Math.max(start,p.start)),0);
 const ourIds=Object.values(users).filter(u=>u.steamId===targetSteamId).map(u=>u.userId);
 if(!ourIds.length){fs.writeFileSync(base+'.audit.json',JSON.stringify({id:item.id,error:'Engineer identity missing'}));continue;}
 let ev=[],ss=[];
 for await(const line of readline.createInterface({input:fs.createReadStream(input+'.json.jsonl'),crlfDelay:Infinity})){
  const v=JSON.parse(line);if(v.kind==='event')ev.push({...v,t:v.tick*dt});
  if(v.kind==='snapshot')ss.push({...v,t:v.tick*dt});
 }
 const at=t=>{let l=0,h=ss.length-1;while(l<h){let m=Math.ceil((l+h)/2);if(ss[m].t<=t)l=m;else h=m-1;}return ss[l];};
 const pa=(u,t)=>at(t)?.players.find(p=>p.user===u);
 const teamAt=t=>at(t).players.find(p=>ourIds.includes(p.user))?.team;
 const starts=ev.filter(e=>e.name==='teamplay_round_active');
 const rounds=starts.map((s,i)=>({n:i+1,start:s.t,end:ev.find(e=>e.name==='teamplay_round_win'&&e.t>s.t&&e.t<(starts[i+1]?.t??Infinity))?.t})).filter(r=>r.end!==undefined);
 const roundAt=t=>rounds.find(r=>r.start<=t&&t<r.end);
 const spawns=ev.filter(e=>e.name==='player_spawn'); const deaths=ev.filter(e=>e.name==='player_death');
 const caps=ev.filter(e=>e.name==='teamplay_point_captured');
 const owner=t=>{const r=roundAt(t);return caps.filter(e=>r&&e.t>=r.start&&e.t<=t).at(-1)?.data.team;};
 // Spawn locations inferred independently from actual spawn events, not hiding players.
 const spawnCenters={};for(const team of ['red','blue']){
  const pts=spawns.filter(e=>roundAt(e.t)&&e.data.team===(team==='red'?2:3)).map(e=>pa(e.data.user_id,e.t+.3)).filter(p=>p?.team===team&&alive(p)).map(p=>p.position);
  spawnCenters[team]={x:med(pts.map(p=>p.x)),y:med(pts.map(p=>p.y)),z:med(pts.map(p=>p.z))};
 }
 const progress=(p,team)=>{const a=spawnCenters[team],b=spawnCenters[team==='red'?'blue':'red'];return ((p.x-a.x)*(b.x-a.x)+(p.y-a.y)*(b.y-a.y))/((b.x-a.x)**2+(b.y-a.y)**2);};
 const ourTeles=s=>s.teles.filter(x=>ourIds.includes(s.players.find(p=>p.entity===(x.extra?.m_hBuilder&2047))?.user));
 // Reset screen: five of the eight non-Spy roles are dead. A surviving rat does not cancel it.
 const wipes=[];let pending=null;
 for(const s of ss){const r=roundAt(s.t);if(!r){pending=null;continue;}const team=teamAt(s.t);if(!['red','blue'].includes(team))continue;
  const ps=s.players.filter(p=>p.team===team&&p.class!=='spy'&&p.class!=='other');
  if(ps.length<7)continue;
  const dead=ps.filter(p=>!alive(p)).length;
  if(dead>=5&&s.t>r.start+20){if(!pending){pending={start:s.t,last_low:s.t,round:r.n,team,max_dead:dead,ground_retake:null};wipes.push(pending);}else{pending.last_low=s.t;pending.max_dead=Math.max(pending.max_dead,dead);}}
  if(pending){
   // Spatial screening only. Three non-Spy teammates reaching >=35% across the map.
   const advanced=ps.filter(p=>alive(p)&&p.in_pvs&&progress(p.position,team)>=.35).length;
   if(advanced>=3&&s.t>pending.last_low+1){pending.ground_retake=s.t;pending=null;}
   else if(elapsed(pending.last_low,s.t)>60)pending=null;
  }
 }
 const teleports=[];
 for(const e of ev.filter(e=>e.name==='player_teleported'&&ourIds.includes(e.data.builder_id)&&roundAt(e.t))){
  const s=at(e.t-.05),p=s.players.find(p=>p.user===e.data.user_id),team=teamAt(e.t);if(!p||p.team!==team)continue;
  const peers=s.players.filter(p=>p.user!==e.data.user_id&&p.team===team&&p.class!=='spy'&&p.class!=='other');
  const entry=ourTeles(s).find(x=>x.tele.is_entrance), exit=ourTeles(s).find(x=>!x.tele.is_entrance);
  const near=peers.filter(p=>alive(p)&&p.in_pvs&&(progress(p.position,team)<.20||(entry&&distance(p.position,entry.tele.position)<600)));
  const dead=peers.filter(p=>!alive(p));
  const w=wipes.filter(w=>w.start<e.t&&w.round===roundAt(e.t).n&&elapsed(Math.min(w.last_low,e.t),e.t)<=45&&(!w.ground_retake||w.ground_retake>e.t)).at(-1);
  const nd=deaths.find(d=>d.data.user_id===e.data.user_id&&d.t>e.t&&d.t<roundAt(e.t).end);
  const ns=spawns.find(d=>d.data.user_id===e.data.user_id&&d.t>e.t&&d.t<roundAt(e.t).end);
  const death=nd&&(!ns||nd.t<ns.t)?nd:null;
  const nextTele=ev.find(x=>x.name==='player_teleported'&&x.data.user_id===e.data.user_id&&x.t>e.t);
  const delay=death?elapsed(e.t,death.t):null;
  const recentSpawn=spawns.filter(x=>x.data.user_id===e.data.user_id&&x.t<e.t).at(-1);
  const damage=ev.filter(x=>x.name==='player_hurt'&&x.data.attacker===e.data.user_id&&x.data.user_id!==e.data.user_id&&x.t>=e.t&&x.t<=Math.min(e.t+10,death?.t??Infinity)).reduce((a,x)=>a+(x.data.damage_amount??0),0);
  // This is contextual evidence for manual review, not a replacement reset
  // classifier. A Medic can also move forward during a prohibited rollout.
  const earlier=at(e.t-1.5);
  const medic=peers.find(x=>x.class==='medic'&&alive(x)&&x.in_pvs);
  const earlierMedic=medic?earlier?.players.find(x=>x.user===medic.user):null;
  const medicProgress=medic?progress(medic.position,team):null;
  const medicProgressChange=medic&&earlierMedic&&alive(earlierMedic)?medicProgress-progress(earlierMedic.position,team):null;
  const medicSpawnDistance=medic?distance(medic.position,spawnCenters[team]):null;
  const medicPeerDistances=medic?peers.filter(x=>x.user!==medic.user&&alive(x)&&x.in_pvs).map(x=>distance(medic.position,x.position)):[];
  const medicNearestPeer=medicPeerDistances.length?Math.min(...medicPeerDistances):null;
  const teamUsers=new Set(s.players.filter(x=>x.team===team).map(x=>x.user));
  const recentFriendlyCombat=ev.some(x=>x.name==='player_hurt'&&x.t>=e.t-2.5&&x.t<=e.t&&x.data.attacker>0&&x.data.attacker!==x.data.user_id&&(teamUsers.has(x.data.attacker)||teamUsers.has(x.data.user_id)));
  const activeMedicSignal=!!medic&&medicSpawnDistance>150&&medicProgressChange!==null&&medicProgressChange>.015&&medicNearestPeer!==null&&medicNearestPeer<=400&&recentFriendlyCombat;
  teleports.push({id:item.id,tick:e.tick,time:rnd(e.t),round:roundAt(e.t).n,user:e.data.user_id,name:users[e.data.user_id]?.name,class:p.class,team,own_point:owner(e.t)===(team==='red'?2:3),near_spawn_other:near.length,dead_other:dead.length,near_names:near.map(x=>users[x.user]?.name),wipe_start:w?rnd(w.start):null,seconds_since_low:w?rnd(e.t-w.last_low):null,from_spawn_s:recentSpawn?rnd(e.t-recentSpawn.t):null,death_s:delay===null?null:rnd(delay),death_tick:death?.tick??null,damage_10s:damage,level:entry?.tele.level,exit_position:exit?.tele.position,strict_candidate:p.class!=='spy'&&!!w&&near.length>=3&&near.length+dead.length>=5,broad_candidate:p.class!=='spy'&&!!w&&near.length+dead.length>=5,active_medic_signal:activeMedicSignal,medic_context:medic?{user:medic.user,progress:rnd(medicProgress),progress_change_1_5s:medicProgressChange===null?null:rnd(medicProgressChange),spawn_distance:rnd(medicSpawnDistance),nearest_living_peer_distance:medicNearestPeer===null?null:rnd(medicNearestPeer),recent_friendly_combat:recentFriendlyCombat}:null,players:s.players.filter(p=>p.team===team).map(p=>({user:p.user,class:p.class,alive:alive(p),progress:rnd(progress(p.position,team)),pos:p.position}))});
 }
 const dets=ev.filter(e=>e.name==='object_detonated'&&ourIds.includes(e.data.user_id)&&e.data.object_type===1&&roundAt(e.t)).map(e=>{const s=at(e.t-.05);const x=ourTeles(s).find(x=>x.tele.entity===e.data.index);return {time:rnd(e.t),tick:e.tick,entrance:x?.tele.is_entrance,operational:x?functional(x):null};});
 const result={version:4,id:item.id,date:item.date,map:source.header.map,duration:source.header.duration,rounds,pauses,active_seconds:rounds.reduce((s,r)=>s+elapsed(r.start,r.end),0),ownIds:ourIds,spawnCenters,wipes,teleports,detonations:dets};
 fs.writeFileSync(base+'.audit.json',JSON.stringify(result));console.log(item.id,'uses',teleports.length,'wipes',wipes.length,'strict',teleports.filter(x=>x.strict_candidate).length,'broad',teleports.filter(x=>x.broad_candidate).length);
}
