use std::{env, fs, io::{BufWriter, Write}, collections::BTreeMap};
use serde_json::{json, Value};
use tf_demo_parser::{Demo, DemoParser, ParserState, MessageType};
use tf_demo_parser::demo::{data::DemoTick, header::Header, message::Message, packet::{stringtable::StringTableEntry, datatable::{ParseSendTable,ServerClass}, message::MessagePacketMeta}, parser::{MessageHandler, analyser::Analyser, gamestateanalyser::{GameStateAnalyser, Building}}};
struct Extractor { summary: Analyser, game: GameStateAnalyser, out: BufWriter<fs::File>, last: u32, extra: BTreeMap<u32,BTreeMap<String,Value>> }
impl Extractor { fn emit(&mut self, value: Value) { serde_json::to_writer(&mut self.out,&value).unwrap(); self.out.write_all(b"\n").unwrap(); } }
impl MessageHandler for Extractor {
 type Output=Value;
 fn does_handle(t:MessageType)->bool { Analyser::does_handle(t)||GameStateAnalyser::does_handle(t)||matches!(t,MessageType::NetTick|MessageType::SetConVar) }
 fn handle_header(&mut self,h:&Header) { self.summary.handle_header(h); self.emit(json!({"kind":"header","data":h})); }
 fn handle_string_entry(&mut self,t:&str,i:usize,e:&StringTableEntry,s:&ParserState) { self.summary.handle_string_entry(t,i,e,s);self.game.handle_string_entry(t,i,e,s); }
 fn handle_data_tables(&mut self,t:&[ParseSendTable],c:&[ServerClass],s:&ParserState) { self.summary.handle_data_tables(t,c,s); self.game.handle_data_tables(t,c,s); }
 fn handle_packet_meta(&mut self,t:DemoTick,m:&MessagePacketMeta,s:&ParserState) { self.summary.handle_packet_meta(t,m,s);self.game.handle_packet_meta(t,m,s); }
 fn handle_message(&mut self,m:&Message,t:DemoTick,s:&ParserState) {
  self.summary.handle_message(m,t,s); self.game.handle_message(m,t,s);
  let tick:u32=t.into();
  match m {
   Message::GameEvent(e)=>self.emit(json!({"kind":"event","tick":tick,"name":e.event_type,"data":e.event})),
   Message::ServerInfo(i)=>self.emit(json!({"kind":"server","tick":tick,"data":i})),
   Message::SetConVar(c)=>self.emit(json!({"kind":"convar","tick":tick,"data":c})),
   Message::PacketEntities(p)=>{
    for e in &p.entities {
     let cn=s.server_classes.get(usize::from(e.server_class)).map(|x|x.name.as_str()).unwrap_or("");
     if cn=="CObjectTeleporter"||cn=="CTFGameRulesProxy" {
      let id:u32=e.entity_index.into();
      let x=self.extra.entry(id).or_default();
      for prop in e.props(s) { if let Some((_,n))=prop.identifier.names() { x.insert(n.to_string(),serde_json::to_value(&prop.value).unwrap()); } }
     }
    }
    if tick>=self.last+16 {
     self.last=tick;
     let players:Vec<Value>=self.game.state.players.iter().map(|p|json!({"entity":p.entity,"user":p.info.as_ref().map(|i|i.user_id),"class":p.class,"team":p.team,"position":p.position,"health":p.health,"state":p.state,"in_pvs":p.in_pvs,"charge":p.charge})).collect();
     let teles:Vec<Value>=self.game.state.buildings.values().filter_map(|b|if let Building::Teleporter(t)=b {let id:u32=t.entity.into();Some(json!({"tele":t,"extra":self.extra.get(&id)}))}else{None}).collect();
     self.emit(json!({"kind":"snapshot","tick":tick,"players":players,"teles":teles,"objectives":self.game.state.objectives}));
    }
   }, _=>{}
  }
 }
 fn into_output(mut self,s:&ParserState)->Value {self.out.flush().unwrap(); json!({"summary":self.summary.into_output(s),"last_tick":self.last})}
}
fn main() {
    let args: Vec<String> = env::args().collect();
    let bytes = fs::read(&args[1]).unwrap();
    let demo = Demo::new(&bytes);
    let extract=Extractor{summary:Analyser::default(),game:GameStateAnalyser::default(),out:BufWriter::new(fs::File::create(format!("{}.jsonl",args[2])).unwrap()),last:0,extra:BTreeMap::new()};
    let parser = DemoParser::new_all_with_analyser(demo.get_stream(),extract);
    let (header, state) = parser.parse().unwrap();
    fs::write(&args[2], serde_json::to_vec(&serde_json::json!({"header":header,"state":state})).unwrap()).unwrap();
}
