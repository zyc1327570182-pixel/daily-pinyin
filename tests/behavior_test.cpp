#include <rime_api.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

RimeApi* api;
RimeSessionId sid;
std::string output;
void drain() {
  RIME_STRUCT(RimeCommit, c);
  if(api->get_commit(sid,&c)) { output += c.text; api->free_commit(&c); }
}
void key(int code,int mask=0) {
  bool handled=api->process_key(sid,code,mask); drain();
  if(!handled && mask==0 && code>=32 && code<127) output.push_back(char(code));
}
void type(const std::string& text) { for(unsigned char c:text) key(c); }
void reset() { api->clear_composition(sid); drain(); output.clear(); api->set_option(sid,"ascii_mode",False); }
std::vector<std::string> candidates() {
  std::vector<std::string> result; RIME_STRUCT(RimeContext,c);
  if(api->get_context(sid,&c)) {
    for(int i=0;i<c.menu.num_candidates;i++) result.push_back(c.menu.candidates[i].text);
    api->free_context(&c);
  }
  return result;
}
void check(bool ok,const std::string& name) { if(!ok) throw std::runtime_error(name+"; output="+output); std::cout<<"PASS\t"<<name<<std::endl; }
int main(int argc,char**argv) {
  if(argc!=2) return 2;
  api=rime_get_api(); RIME_STRUCT(RimeTraits,t);
  t.user_data_dir=argv[1]; t.shared_data_dir=argv[1];
  t.app_name="rime.dailytest";t.min_log_level=2;t.log_dir="";
  api->setup(&t);api->initialize(&t);
  if(api->start_maintenance(False))api->join_maintenance_thread();
  sid=api->create_session(); if(!api->select_schema(sid,"wanxiang"))return 3;
  try {
    for(auto pair:std::vector<std::pair<std::string,std::string>>{
        {"nihao","你好"},{"jintianwanshangyiqichifan","今天晚上一起吃饭"},
        {"mingtianshangwujiudianbankaihui","明天上午九点半开会"},
        {"woxiangyaoyigegenghaoyongdeshurufa","我想要一个更好用的输入法"}}) {
      reset();type(pair.first);key(' ');check(output==pair.second,"space commit: "+pair.second);
    }
    for(int shift:{0xffe1,0xffe2}) {
      reset();type("hello"); check(output.empty(),"English code remains uncommitted before Shift");
      key(shift);key(shift,1<<30);
      check(output=="hello" && api->get_option(sid,"ascii_mode"),"Shift commits original English and switches mode");
      type("world");check(output=="helloworld","English input continues immediately");
      key(shift);key(shift,1<<30);check(!api->get_option(sid,"ascii_mode"),"Shift switches back to Chinese");
    }
    reset();type("nihaoo");key(0xff08);auto cs=candidates();check(!cs.empty()&&cs[0]=="你好","Backspace repairs composition");
    key(0xff1b);check(candidates().empty()&&output.empty(),"Escape cancels without committing");
    reset();type("hello");key(0xff0d);check(output=="hello","Enter commits original code");
    reset();type("nihao");cs=candidates();check(cs.size()==5,"Five visible candidates");
    std::string second=cs.at(1);key('2');check(output==second,"Number 2 selects second candidate");
    reset();type("nihao");cs=candidates();check(!cs.empty()&&cs[0]==second,"Selected word is promoted by user learning");
    reset();type("shi");key(0xff56);RIME_STRUCT(RimeContext,c);
    bool page=api->get_context(sid,&c)&&c.menu.page_no==1;api->free_context(&c);check(page,"PageDown changes candidate page");
    reset();type("shurufa,");check(output=="输入法，","Chinese punctuation commits composition");
    reset();key(0xffe5);check(!api->get_option(sid,"ascii_mode"),"Caps Lock does not toggle input language");
  } catch(const std::exception&e) { std::cerr<<"FAIL\t"<<e.what()<<std::endl;api->destroy_session(sid);api->finalize();return 1; }
  api->destroy_session(sid);api->finalize();
}
