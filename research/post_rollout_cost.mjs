import fs from 'node:fs';
const dt=.015,rnd=x=>Math.round(x*100)/100,alive=p=>p.state==='Alive'&&p.health>0;
const speed={engineer:300,pyro:300,sniper:300,heavy:230,medic:320};
const rows=[];
for(const [id,map] of [[1502837,'product'],[1502830,'ashville']]){
 const raw=fs.readFileSync(`research/${map}.json.jsonl`,'utf8').trim().split('\n').map(JSON.parse);
 const ss=raw.filter(x=>x.kind==='snapshot').map(s=>({...s,t:s.tick*dt}));
 const ev=raw.filter(x=>x.kind==='event').map(s=>({...s,t:s.tick*dt}));
 const a=JSON.parse(fs.readFileSync(`research/${map}_analysis.json`));
 const audit=JSON.parse(fs.readFileSync(`research/history/${id}.audit.json`));
 const lives=JSON.parse(fs.readFileSync(`research/${map}_lives.json`));
 const at=t=>{let l=0,h=ss.length-1;while(l<h){let m=Math.ceil((l+h)/2);if(ss[m].t<=t)l=m;else h=m-1;}return ss[l];};
 const center=audit.spawnCenters.blue,other=audit.spawnCenters.red;
 const progress=p=>((p.x-center.x)*(other.x-center.x)+(p.y-center.y)*(other.y-center.y))/((other.x-center.x)**2+(other.y-center.y)**2);
 const caps=ev.filter(e=>e.name==='teamplay_point_captured');
 const ownAt=(t,r)=>caps.filter(c=>c.t>=r.start&&c.t<=t).at(-1)?.data.team===3;
 for(const d of a.detonations.filter(d=>d.end==='exit'&&d.old_pair_functional)){
  const r=a.rounds.find(r=>r.n===d.round),end=d.next_pair_ready_s??r.end;
  for(const threshold of [3,4]){
   // Reopening proxy: 3 or 4 non-Spy teammates >=35% across map for two seconds.
   // This is terrain recovery evidence, not proof that a tele exit is safe.
   let first=null,reopen=null;
   for(const s of ss.filter(s=>s.t>=d.demo_s&&s.t<end)){
    const n=s.players.filter(p=>p.team==='blue'&&p.class!=='spy'&&alive(p)&&p.in_pvs&&progress(p.position)>=.35).length;
    if(n>=threshold){if(first===null)first=s.t;if(s.t-first>=2){reopen=s.t;break;}}else first=null;
   }
   const cutoff=end;
   const candidates=reopen===null?[]:lives.filter(l=>l.team===3&&l.death_s>=reopen&&l.spawn_s<cutoff&&l.spawn_s>reopen);
   let nextReady=reopen??end;const transfers=[];
   for(const l of candidates.sort((a,b)=>a.spawn_s-b.spawn_s)){
    if(!speed[l.class])continue;
    const ratio=300/speed[l.class];
    const entryAt=l.spawn_s+2*ratio,send=Math.max(entryAt,nextReady),queueWait=send-entryAt;
    const groundNow=ss.filter(s=>s.t>=send-2&&s.t<=send).every(s=>s.players.filter(p=>p.team==='blue'&&p.class!=='spy'&&alive(p)&&p.in_pvs&&progress(p.position)>=.35).length>=threshold);
    if(!groundNow)continue;
    const arrivalTele=send+.6+(map==='product'?4:3)*ratio;
    const arrivalWalk=l.spawn_s+12*ratio;
    if(queueWait>1||arrivalTele>=arrivalWalk||arrivalTele>=cutoff)continue;
    nextReady=send+([0,10.6,5.6,3.6][d.old_level]);
    const usableEnd=Math.min(arrivalWalk,l.next_death_s,cutoff);
    const saved=Math.max(0,usableEnd-arrivalTele);
    const attack=!ownAt(l.spawn_s,r);
    const attackEnd=caps.find(c=>c.t>l.spawn_s&&c.data.team===3)?.t??cutoff;
    const attackSaved=attack?Math.max(0,Math.min(usableEnd,attackEnd)-arrivalTele):0;
    transfers.push({user:l.user,class:l.class,death:l.death_s,spawn:l.spawn_s,queue_wait:rnd(queueWait),tele_arrival:rnd(arrivalTele),walk_arrival:rnd(arrivalWalk),saved:rnd(saved),attack_saved:rnd(attackSaved)});
   }
   rows.push({map,destruction:d.demo_s,level:d.old_level,threshold,reopen:reopen===null?null:rnd(reopen),connection_back:end,post_retake_respawns:candidates.length,model_rides:transfers.length,saved:rnd(transfers.reduce((s,t)=>s+t.saved,0)),attack_saved:rnd(transfers.reduce((s,t)=>s+t.attack_saved,0)),transfers});
  }
 }
}
fs.writeFileSync('research/post_rollout_cost.json',JSON.stringify(rows,null,2));
for(const threshold of [3,4]){let a=rows.filter(x=>x.threshold===threshold);console.log(threshold,JSON.stringify({rides:a.reduce((s,x)=>s+x.model_rides,0),saved:rnd(a.reduce((s,x)=>s+x.saved,0)),attack_saved:rnd(a.reduce((s,x)=>s+x.attack_saved,0)),cases:a.filter(x=>x.model_rides)}));}
