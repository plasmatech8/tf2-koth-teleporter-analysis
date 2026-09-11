import fs from 'node:fs';
import readline from 'node:readline';
const dir='research/history',dt=.015,rnd=x=>Math.round(x*100)/100;
const alive=p=>p.state==='Alive'&&p.health>0;
const speed={engineer:300,pyro:300,sniper:300,heavy:230,medic:320};
const classes=['other','scout','sniper','soldier','demoman','medic','heavy','pyro','spy','engineer'];
const audits=fs.readdirSync(dir).filter(f=>f.endsWith('.audit.json')).map(f=>JSON.parse(fs.readFileSync(dir+'/'+f))).filter(a=>a.id>1494495);
let result=[];
for(const a of audits){
 const input=a.id===1502837?'research/product':`${dir}/${a.id}`;
 let ss=[],ev=[];
 for await(const line of readline.createInterface({input:fs.createReadStream(input+'.json.jsonl'),crlfDelay:Infinity})){
  const v=JSON.parse(line);if(v.kind==='snapshot')ss.push({...v,t:v.tick*dt});if(v.kind==='event')ev.push({...v,t:v.tick*dt});
 }
 const at=t=>{let l=0,h=ss.length-1;while(l<h){let m=Math.ceil((l+h)/2);if(ss[m].t<=t)l=m;else h=m-1;}return ss[l];};
 const ownTeles=s=>s.teles.filter(x=>a.ownIds.includes(s.players.find(p=>p.entity===(x.extra?.m_hBuilder&2047))?.user));
 const func=x=>!x.tele.building&&!x.tele.sapped&&!x.extra?.m_bDisabled&&!x.extra?.m_bCarried&&!x.extra?.m_bPlacing&&[2,3,4,5,6].includes(x.extra?.m_iState);
 const pair=s=>{let x=ownTeles(s);return x.some(x=>x.tele.is_entrance&&func(x))&&x.some(x=>!x.tele.is_entrance&&func(x));};
 const roundAt=t=>a.rounds.find(r=>r.start<=t&&t<r.end);
 const spawns=ev.filter(e=>e.name==='player_spawn'), deaths=ev.filter(e=>e.name==='player_death'),caps=ev.filter(e=>e.name==='teamplay_point_captured');
 const life=[];for(const s of spawns){const r=roundAt(s.t);if(!r)continue;const d=deaths.filter(e=>e.data.user_id===s.data.user_id&&e.t<s.t&&e.t>=r.start).at(-1);if(!d||spawns.some(e=>e.data.user_id===s.data.user_id&&e.t>d.t&&e.t<s.t))continue;
  life.push({user:s.data.user_id,team:s.data.team,class:classes[s.data.class],death:d.t,spawn:s.t,next_death:deaths.find(e=>e.data.user_id===s.data.user_id&&e.t>s.t)?.t??r.end});}
 for(const d of a.detonations.filter(d=>d.entrance===false)){
  const s=at(d.time-.1);if(!pair(s))continue;
  const exit=ownTeles(s).find(x=>!x.tele.is_entrance),entry=ownTeles(s).find(x=>x.tele.is_entrance);
  const team=s.players.find(p=>a.ownIds.includes(p.user))?.team;if(!['blue','red'].includes(team))continue;
  const r=roundAt(d.time),stop=ss.find(s=>s.t>d.time+.1&&s.t<r.end&&pair(s))?.t??r.end;
  const startCenter=a.spawnCenters[team],enemyCenter=a.spawnCenters[team==='blue'?'red':'blue'];
  const progress=p=>((p.x-startCenter.x)*(enemyCenter.x-startCenter.x)+(p.y-startCenter.y)*(enemyCenter.y-startCenter.y))/((enemyCenter.x-startCenter.x)**2+(enemyCenter.y-startCenter.y)**2);
  const advanced=s=>s.players.filter(p=>p.team===team&&p.class!=='spy'&&p.class!=='other'&&alive(p)&&p.in_pvs&&progress(p.position)>=.35).length;
  for(const threshold of [3,4])for(const maintained of [false,true]){
   let first=null,reopen=null;for(const s of ss.filter(s=>s.t>=d.time&&s.t<stop)){if(advanced(s)>=threshold){if(first===null)first=s.t;if(s.t-first>=2){reopen=s.t;break;}}else first=null;}
   const row={id:a.id,map:a.map,destruction:d.time,tick:d.tick,threshold,maintained,reopen:reopen===null?null:rnd(reopen),restored:rnd(stop),level:entry.tele.level,rides:[]};
   if(reopen!==null){let ready=reopen;
    const cand=life.filter(l=>l.team===(team==='blue'?3:2)&&l.spawn>=reopen&&l.spawn<stop&&speed[l.class]);
    for(const l of cand){const ratio=300/speed[l.class],entryAt=l.spawn+2*ratio,send=Math.max(entryAt,ready),queueWait=send-entryAt;
     if(maintained&&!ss.filter(s=>s.t>=send-2&&s.t<=send).every(s=>advanced(s)>=threshold))continue;
     const via=send+.6+(a.map.includes('product')?4:3)*ratio,walk=l.spawn+12*ratio;
     if(queueWait>1||via>=walk||via>=stop)continue;
     ready=send+([0,10.6,5.6,3.6][entry.tele.level]);
     const end=Math.min(walk,l.next_death,stop),saved=Math.max(0,end-via);
     const owner=caps.filter(e=>e.t>=r.start&&e.t<=l.spawn).at(-1)?.data.team;
     const attacking=owner===(team==='blue'?2:3);
     const attackEnd=caps.find(e=>e.t>l.spawn&&e.data.team===(team==='blue'?3:2))?.t??stop;
     const attackSaved=attacking?Math.max(0,Math.min(end,attackEnd)-via):0;
     row.rides.push({...l,death_after_retake:l.death>=reopen,queue_wait:rnd(queueWait),tele_arrival:rnd(via),walk_arrival:rnd(walk),saved:rnd(saved),attack_saved:rnd(attackSaved)});
    }
   }
   result.push(row);
  }
 }
 console.log(a.id,'processed');
}
fs.writeFileSync(dir+'/cost_scenarios.json',JSON.stringify(result,null,2));
const sum=[];for(const threshold of [3,4])for(const maintained of [false,true]){let rows=result.filter(r=>r.threshold===threshold&&r.maintained===maintained),rides=rows.flatMap(r=>r.rides);sum.push({threshold,maintained,demos:audits.length,operational_destructions:rows.length,rides:rides.length,attack_rides:rides.filter(r=>r.attack_saved>0).length,saved:rnd(rides.reduce((s,r)=>s+r.saved,0)),attack_saved:rnd(rides.reduce((s,r)=>s+r.attack_saved,0))});}
fs.writeFileSync(dir+'/cost_summary.json',JSON.stringify(sum,null,2));console.log(sum);
