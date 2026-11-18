#include <rime_api.h>
#include <algorithm>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
RimeApi* api;RimeSessionId sid=0;std::string output;
void drain(){RIME_STRUCT(RimeCommit,c);if(api->get_commit(sid,&c)){output+=c.text;api->free_commit(&c);}}
bool key(int code,int mask=0){bool handled=api->process_key(sid,code,mask);drain();if(!handled&&mask==0&&code>=32&&code<127)output+=char(code);return handled;}
void type(std::string s){for(unsigned char c:s)key(c);}
std::vector<std::string> choices(){RIME_STRUCT(RimeContext,c);std::vector<std::string> v;if(api->get_context(sid,&c)){for(int i=0;i<c.menu.num_candidates;i++)v.push_back(c.menu.candidates[i].text);api->free_context(&c);}return v;}
bool predicted(){RIME_STRUCT(RimeContext,c);bool yes=api->get_context(sid,&c)&&c.composition.length==0&&c.menu.num_candidates>0;api->free_context(&c);return yes;}
void fresh(){if(sid)api->destroy_session(sid);sid=api->create_session();if(!api->select_schema(sid,"wanxiang"))throw std::runtime_error("schema missing");api->set_option(sid,"ascii_mode",false);api->set_option(sid,"prediction",true);output.clear();}
void commit(std::string code,std::string expected){type(code);key(' ');if(output!=expected)throw std::runtime_error("wrong initial commit: "+output);}
void check(bool yes,std::string name){if(!yes)throw std::runtime_error(name+"; output="+output);std::cout<<"PASS\t"<<name<<std::endl;}
int main(int argc,char**argv){if(argc!=2)return 2;api=rime_get_api();RIME_STRUCT(RimeTraits,t);t.user_data_dir=argv[1];t.shared_data_dir=argv[1];t.app_name="rime.predictiontest";t.min_log_level=2;t.log_dir="";api->setup(&t);api->initialize(&t);if(api->start_maintenance(false))api->join_maintenance_thread();try{
 fresh();check(choices().empty(),"new context does not show unsolicited predictions");commit("jintian","今天");check(predicted(),"committing Chinese opens next-word candidates");auto v=choices();check(v.size()<=5,"at most five prediction candidates");check(std::find(v.begin(),v.end(),"晚上")!=v.end(),"today has an evening continuation");std::cout<<"CANDIDATES\t今天";for(auto w:v)std::cout<<"\t"<<w;std::cout<<std::endl;
 std::string second=v.at(1);key('2');check(output=="今天"+second,"number selects intended prediction without repeating previous text");
 fresh();commit("jintian","今天");v=choices();key(0xff54);key(0xff54);key(0xff0d);check(output=="今天"+v.at(1),"Down and Enter select the next word");
 fresh();commit("jintian","今天");v=choices();bool enterHandled=key(0xff0d);check(!enterHandled && output=="今天"&&!predicted(),"unarmed Enter preserves application Send/Newline without accepting a prediction");
 fresh();commit("jintian","今天");key(' ');check(output=="今天 "&&!predicted(),"Space inserts a literal space and dismisses predictions");key(' ',1<<30);check(!predicted(),"key release does not reopen dismissed predictions");
 fresh();commit("jintian","今天");type("wanshang");check(!predicted()&&choices().at(0)=="晚上","typing replaces predictions with regular Pinyin immediately");key(' ');check(output=="今天晚上","continuing Pinyin does not lose or duplicate a character");
 fresh();commit("jintian","今天");key(',');check(output=="今天，"&&!predicted(),"punctuation does not accidentally select a prediction");
 fresh();commit("jintian","今天");key('9');check(output=="今天9"&&!predicted(),"out-of-range digit is entered literally");
 fresh();commit("jintian","今天");key(0xff1b);check(output=="今天"&&choices().empty(),"Escape dismisses predictions without extra output");type("nihao");key(' ');check(output=="今天你好","typing resumes after Escape");
 fresh();commit("jintian","今天");key(0xff08);check(output=="今天"&&choices().empty(),"Backspace dismisses without inserting anything");
 for(int shift:{0xffe1,0xffe2}){fresh();commit("jintian","今天");key(shift);key(shift,1<<30);check(api->get_option(sid,"ascii_mode")&&!predicted(),"Shift switches to English and clears predictions");type("hello");check(output=="今天hello","English letters remain literal after prediction");key(shift);key(shift,1<<30);check(!api->get_option(sid,"ascii_mode")&&!predicted(),"returning to Chinese does not resurrect old predictions");}
 fresh();commit("jintian","今天");api->clear_composition(sid);check(choices().empty(),"external reset/focus change does not resurrect old predictions");
 fresh();commit("jintian","今天");api->set_option(sid,"prediction",false);check(choices().empty(),"turning prediction off dismisses an already visible suggestion");
 fresh();api->set_option(sid,"prediction",false);commit("jintian","今天");check(choices().empty(),"prediction switch disables suggestions");
 fresh();commit("womentongyi","我们同意");check(predicted(),"sentence commit can predict from its ending");
 fresh();type("hello");key(0xffe1);key(0xffe1,1<<30);check(output=="hello"&&api->get_option(sid,"ascii_mode")&&!predicted(),"Shift still preserves partially typed English");
 fresh();commit("xiexie","谢谢");v=choices();check(!v.empty()&&v[0]=="你","thanks predicts a natural continuation");std::cout<<"CANDIDATES\t谢谢";for(auto w:v)std::cout<<"\t"<<w;std::cout<<std::endl;
 fresh();commit("jintian","今天");int accepted=0;while(predicted()&&accepted<8){key('1');accepted++;}check(accepted>0&&accepted<=3,"prediction chaining stops at the configured limit");
 }catch(const std::exception&e){std::cerr<<"FAIL\t"<<e.what()<<std::endl;if(sid)api->destroy_session(sid);api->finalize();return 1;}if(sid)api->destroy_session(sid);api->finalize();return 0;}
