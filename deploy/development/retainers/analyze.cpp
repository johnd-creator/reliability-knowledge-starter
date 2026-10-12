// Bounded private V8 snapshot graph analyzer. Public output is allowlisted/numeric.
// Strong-edge dominators are graph measurements, NOT a full ephemeron-GC simulator.
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
struct Reader {
 bool inlineMap=false;uint64_t chars=0;string tail;ifstream f;Reader(const string&p):f(p) {if(!f)throw runtime_error("input");}
 void ws(){while(isspace(f.peek()))f.get();} void expect(char c){ws();if(f.get()!=c)throw runtime_error("schema");}
 string str(){expect('"');inlineMap=false;chars=0;tail.clear();string s;bool esc=false;while(true){int c=f.get();if(c<0)throw runtime_error("truncated");if(!esc&&c=='"')break;if(!esc&&c=='\\'){esc=true;continue;}if(esc){if(c=='u'){for(int i=0;i<4;i++)if(f.get()<0)throw runtime_error("escape");c='?';}else if(c=='n')c='\n';else if(c=='r')c='\r';else if(c=='t')c='\t';esc=false;}chars++;if(s.size()<512)s+=(char)c;if(!inlineMap){tail+=(char)c;if(tail.size()>64)tail.erase(0,1);if(tail.find("sourceMappingURL=data:application/json")!=string::npos)inlineMap=true;}}return s;}
 uint64_t num(){ws();uint64_t n=0;bool any=false;while(isdigit(f.peek())){any=true;auto digit=f.get()-'0';if(n>(UINT64_MAX-digit)/10)throw runtime_error("number overflow");n=n*10+digit;}if(!any)throw runtime_error("number");return n;}
 string value(){ws();string s;int c=f.peek();if(c!='{'&&c!='['){skip();return s;}int depth=0;bool quoted=false,esc=false;do{c=f.get();if(c<0)throw runtime_error("truncated");if(s.size()<16000)s+=(char)c;if(quoted){if(esc)esc=false;else if(c=='\\')esc=true;else if(c=='"')quoted=false;}else if(c=='"')quoted=true;else if(c=='{'||c=='[')depth++;else if(c=='}'||c==']')depth--;}while(depth);return s;}
 void skip(){ws();int c=f.peek();if(c=='"'){str();return;}if(c=='{'||c=='['){value();return;}while(f&&f.peek()!=','&&f.peek()!=']'&&f.peek()!='}'&&!isspace(f.peek()))f.get();}
 bool comma(){ws();if(f.peek()==','){f.get();return true;}return false;}
};
struct Node{uint32_t type,name,count;uint64_t id,self;};
struct Edge{uint32_t type,name,to;};
const vector<string> types={"hidden","array","string","object","code","closure","regexp","number","native","synthetic","concatenated string","sliced string","symbol","bigint","object shape"};
const vector<string> edgeTypes={"context","element","property","internal","hidden","shortcut","weak"};
set<string> labels={"(GC roots)","(Global handles)","(Stack roots)","(Strong roots)","(Read-only roots)","(Smi roots)","(Internalized strings)","(External strings)","(Builtins)","(Global object)","global","Map","WeakMap","WeakRef","Object","Array","SourceMap","Module","Compiler","Compilation","ModuleGraph","MemoryWithGcCachePlugin","LRUCache","LRUCacheWithTTL","Promise","NativeModule","Context","system / Context","system / NativeContext","system / Script","system / SharedFunctionInfo","system / JSReceiver","defaultLoadImpl","collectStackTracePrivate","init","before","promiseResolve","destroy","getModuleContext","sourceMapFromFile","findSourceMap","getModuleSourceMapCache","generatedSourceMapCache","SourceMapCacheMap","SafeWeakMap","SafeMap","prepareStackTrace","wrappedPrepareStackTrace","console","wrapperMethod","Viewport","fetch","retrieveSourceMap","mapSourcePosition","captureStackTrace","webpackRequire","require","SYNTHETIC_TEST_ROOT","SYNTHETIC_OWNER","SYNTHETIC_SHARED","SYNTHETIC_LEAF"};
set<string> edgeLabels={"pendingOperations","previous","awaited","jsxPropsParents","console","dirxml","wrapperMethod","fetch","_N_E_STYLE_LOAD","stack","owner","promise","sourceMapCache","cjsSourceMapCache","esmSourceMapCache","generatedSourceMapCache","getModuleSourceMapCache","sourceMap","prepareStackTrace","moduleSourceMapCache","stackTraceCache","source","sourcesContent","payload","table","context","script","shared","function_data","native_context","source_map_url","exports","_cache","cache","modules","compilation","moduleContexts","filename","children","parent","__NADI_DIAGNOSTIC_OPERATIONS","SYNTHETIC_TEST_ROOT","child","left","right"};
string safe(const string&s,const string&fallback){return labels.count(s)?s:fallback;}
int main(int argc,char**argv){try{
 bool details=argc==3&&string(argv[2])=="--private-details";if(argc!=2&&!details){throw runtime_error("args");}
 auto p=filesystem::path(argv[1]);if(filesystem::is_symlink(p)||!p.is_absolute()||filesystem::canonical(p).string().rfind("/tmp/nadi-fix05-private/",0)!=0||filesystem::file_size(p)>384ull*1024*1024)throw runtime_error("private budget");
 Reader r(p.string());vector<Node> nodes;vector<Edge> edges;vector<string> strings;vector<bool> inlineMaps;vector<uint64_t> stringChars;uint32_t declaredN=0,declaredE=0;
 r.expect('{');do{string key=r.str();r.expect(':');
  if(key=="snapshot") {r.expect('{');do{auto k=r.str();r.expect(':');if(k=="meta"){auto meta=r.value();string compact;bool q=false,esc=false;for(char c:meta){if(q){compact+=c;if(esc)esc=false;else if(c=='\\')esc=true;else if(c=='"')q=false;}else if(c=='"'){q=true;compact+=c;}else if(!isspace(c))compact+=c;}if(compact.find("\"node_fields\":[\"type\",\"name\",\"id\",\"self_size\",\"edge_count\",\"trace_node_id\",\"detachedness\"]")==string::npos||compact.find("\"edge_fields\":[\"type\",\"name_or_index\",\"to_node\"]")==string::npos||compact.find("\"node_types\":[[\"hidden\",\"array\",\"string\",\"object\",\"code\",\"closure\",\"regexp\",\"number\",\"native\",\"synthetic\",\"concatenated string\",\"sliced string\",\"symbol\",\"bigint\",\"object shape\"]")==string::npos||compact.find("\"edge_types\":[[\"context\",\"element\",\"property\",\"internal\",\"hidden\",\"shortcut\",\"weak\"]")==string::npos)throw runtime_error("V8 meta");}else if(k=="node_count")declaredN=r.num();else if(k=="edge_count")declaredE=r.num();else r.skip();}while(r.comma());r.expect('}');if(declaredN>4000000||declaredE>20000000)throw runtime_error("graph budget");}
  else if(key=="nodes") {r.expect('[');if(declaredN)nodes.reserve(declaredN);do{uint32_t t=r.num();r.expect(',');uint32_t name=r.num();r.expect(',');auto id=r.num();r.expect(',');auto self=r.num();r.expect(',');uint32_t count=r.num();r.expect(',');r.num();r.expect(',');r.num();nodes.push_back({t,name,count,id,self});if(nodes.size()>4000000)throw runtime_error("nodes budget");}while(r.comma());r.expect(']');}
  else if(key=="edges") {r.expect('[');edges.reserve(declaredE);do{uint32_t t=r.num();r.expect(',');uint32_t name=r.num();r.expect(',');auto to=r.num();if(to%7)throw runtime_error("node alignment");edges.push_back({t,name,(uint32_t)(to/7)});if(edges.size()>20000000)throw runtime_error("edges budget");}while(r.comma());r.expect(']');}
  else if(key=="strings"){r.expect('[');do{strings.push_back(r.str());inlineMaps.push_back(r.inlineMap);stringChars.push_back(r.chars);if(strings.size()>2000000)throw runtime_error("strings budget");}while(r.comma());r.expect(']');}
  else r.skip();
 }while(r.comma());r.expect('}');if(nodes.empty()||nodes.size()!=declaredN||edges.size()!=declaredE)throw runtime_error("counts");
 uint32_t n=nodes.size();map<string,uint64_t> typeBytes;for(auto&node:nodes)if(node.type<types.size())typeBytes[types[node.type]]+=node.self;vector<uint32_t> offset(n+1);uint64_t total=0;for(uint32_t i=0;i<n;i++){if(nodes[i].count>edges.size()||uint64_t(offset[i])+nodes[i].count>edges.size())throw runtime_error("edge count overflow");offset[i+1]=offset[i]+nodes[i].count;total+=nodes[i].self;if(nodes[i].name>=strings.size()||nodes[i].type>=types.size())throw runtime_error("node index");}if(offset[n]!=edges.size())throw runtime_error("edge range");for(auto&e:edges)if(e.to>=n||e.type>=7||((e.type!=1&&e.type!=4)&&e.name>=strings.size()))throw runtime_error("edge index");
 auto strong=[&](uint32_t from,const Edge&e){return e.type!=6&&(e.type!=5||from==0);};
 auto ename=[&](const Edge&e)->string{return (e.type==1||e.type==4)?"[index]":strings[e.name];};
 auto label=[&](uint32_t i)->string{
 auto&s=strings[nodes[i].name];
 if(nodes[i].type==4){
  if(s.find("app-page.runtime.dev.js")!=string::npos)return "Next.app-page.runtime.dev";
  if(s.find("bundle5.js")!=string::npos)return "Webpack.bundle5";
  if(s.find("vendor-chunks/next.js")!=string::npos)return "Webpack.vendor.next";
  if(s.find("webpack-runtime.js")!=string::npos)return "Webpack.runtime";
  if(s.find("source_map_cache")!=string::npos)return "Node.source-map-cache";
 }
 if(details&&nodes[i].type!=2&&nodes[i].type!=10&&nodes[i].type!=11&&s.size()<80&&s.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$ .-/()") == string::npos&&s.find('/')==string::npos)return s;
 return safe(s,"<"+types[nodes[i].type]+">");};
 // DFS numbering and spanning-tree paths. Root shortcuts only, all weak edges excluded.
 vector<uint32_t> number(n),vertex(1),parent(1),dfsNode{0},dfsEdge{offset[0]},bfsParent(n,UINT32_MAX),bfsEdge(n,UINT32_MAX);number[0]=1;vertex.push_back(0);parent.push_back(0);
 while(!dfsNode.empty()){uint32_t u=dfsNode.back(),&idx=dfsEdge.back();if(idx==offset[u+1]){dfsNode.pop_back();dfsEdge.pop_back();continue;}auto e=edges[idx++];if(!strong(u,e)||number[e.to])continue;number[e.to]=vertex.size();vertex.push_back(e.to);parent.push_back(number[u]);dfsNode.push_back(e.to);dfsEdge.push_back(offset[e.to]);}
 uint32_t k=vertex.size()-1;vector<uint32_t> predOff(k+2);for(uint32_t u=0;u<n;u++)if(number[u])for(uint32_t j=offset[u];j<offset[u+1];j++)if(strong(u,edges[j])&&number[edges[j].to])predOff[number[edges[j].to]+1]++;
 for(uint32_t i=1;i<predOff.size();i++){predOff[i]+=predOff[i-1];}
 vector<uint32_t> pred(predOff.back()),cursor=predOff;
 for(uint32_t u=0;u<n;u++)if(number[u])for(uint32_t j=offset[u];j<offset[u+1];j++)if(strong(u,edges[j])&&number[edges[j].to])pred[cursor[number[edges[j].to]]++]=number[u];
 vector<uint32_t> semi(k+1),dom(k+1),ancestor(k+1),lab(k+1),head(k+1),next(k+1),chain;for(uint32_t i=1;i<=k;i++)semi[i]=lab[i]=i;
 auto eval=[&](uint32_t v){if(!ancestor[v])return lab[v];chain.clear();uint32_t x=v;while(ancestor[x]&&ancestor[ancestor[x]]){chain.push_back(x);x=ancestor[x];}for(auto it=chain.rbegin();it!=chain.rend();++it){x=*it;if(semi[lab[ancestor[x]]]<semi[lab[x]])lab[x]=lab[ancestor[x]];ancestor[x]=ancestor[ancestor[x]];}return lab[v];};
 for(uint32_t w=k;w>1;w--){for(uint32_t j=predOff[w];j<predOff[w+1];j++){auto u=eval(pred[j]);semi[w]=min(semi[w],semi[u]);}next[w]=head[semi[w]];head[semi[w]]=w;ancestor[w]=parent[w];uint32_t v=head[parent[w]];head[parent[w]]=0;while(v){auto u=eval(v);dom[v]=semi[u]<semi[v]?u:parent[w];v=next[v];}}
 for(uint32_t i=2;i<=k;i++)if(dom[i]!=semi[i])dom[i]=dom[dom[i]];
 vector<uint64_t> retained(k+1);for(uint32_t i=1;i<=k;i++)retained[i]=nodes[vertex[i]].self;for(uint32_t i=k;i>1;i--)retained[dom[i]]+=retained[i];
 // Shortest strong paths, independent from dominator paths.
 vector<uint32_t> queue{0};bfsParent[0]=0;for(size_t q=0;q<queue.size();q++){auto u=queue[q];for(uint32_t j=offset[u];j<offset[u+1];j++)if(strong(u,edges[j])&&bfsParent[edges[j].to]==UINT32_MAX){bfsParent[edges[j].to]=u;bfsEdge[edges[j].to]=j;queue.push_back(edges[j].to);}}
 map<string,vector<uint32_t>> roots;map<string,set<uint32_t>> originStrings;map<string,uint64_t> originScripts;vector<bool> isSource(n),isMapUrl(n);vector<uint32_t> large,mapUrls;uint64_t sourceBytes=0;
 for(uint32_t u=0;u<n;u++){
  const auto& name=strings[nodes[u].name];if(name=="SourceMap"&&nodes[u].type==3)roots["SourceMap.instances"].push_back(u);if((nodes[u].type==3||nodes[u].type==5)&&(name=="SourceMapCacheMap"||name=="getModuleSourceMapCache"))roots["Node.sourceMapCache"].push_back(u);if((nodes[u].type==3||nodes[u].type==5)&&(name=="Compiler"||name=="Compilation"||name=="ModuleGraph"||name=="MemoryWithGcCachePlugin"))roots["Webpack.objects"].push_back(u);
  for(uint32_t j=offset[u];j<offset[u+1];j++){
   auto key=ename(edges[j]);auto to=edges[j].to;if(key=="pendingOperations")roots["Flight.pendingOperations"].push_back(to);
   if(key=="fetch"&&name=="global")roots["Next.global.fetch"].push_back(to);
   if(key=="_N_E_STYLE_LOAD"&&name=="global")roots["Next.global.style"].push_back(to);
   if(key=="dirxml"&&name=="console")roots["React.console.dirxml"].push_back(to);
   if(key=="generatedSourceMapCache")roots["Node.sourceMapCache"].push_back(to);
   if(key=="cjsSourceMapCache"||key=="esmSourceMapCache"||key=="sourceMapCache"||key=="moduleSourceMapCache")roots["SourceMap.namedCaches"].push_back(to);
   if(key=="moduleContexts"||key=="_cache")roots["Module.caches"].push_back(to);
   if(key=="source"&&(name=="system / Script"||nodes[u].type==4)){isSource[to]=true;if(nodes[to].self>=65536){auto origin=label(u);originStrings[origin].insert(to);originScripts[origin]++;}}
   if(key=="source_map_url")isMapUrl[to]=true;
   if(key=="sourcesContent")for(uint32_t j2=offset[to];j2<offset[to+1];j2++)if(edges[j2].type==1)isSource[edges[j2].to]=true;
  }
 }
 for(uint32_t i=0;i<n;i++)if(nodes[i].type==2||nodes[i].type==10||nodes[i].type==11){auto&s=strings[nodes[i].name];bool code=s.find("__webpack")!=string::npos||s.rfind("\"use strict\"",0)==0||s.rfind("'use strict'",0)==0||s.rfind("(function",0)==0;if(nodes[i].self>=65536&&(code||isSource[i])){isSource[i]=true;large.push_back(i);sourceBytes+=nodes[i].self;}}
 uint64_t mapUrlBytes=0;for(uint32_t i=0;i<n;i++)if((nodes[i].type==2||nodes[i].type==10||nodes[i].type==11)&&nodes[i].self>=65536&&(isMapUrl[i]||strings[nodes[i].name].rfind("data:application/json",0)==0)){mapUrls.push_back(i);mapUrlBytes+=nodes[i].self;}
 // Only count measured large source strings, not incidental small source keys.
 vector<bool> counted(n);for(auto i:large)counted[i]=true;
 vector<uint64_t> sourceDominated(k+1);for(auto i:large)if(number[i])sourceDominated[number[i]]=nodes[i].self;for(uint32_t i=k;i>1;i--)sourceDominated[dom[i]]+=sourceDominated[i];
 uint64_t inlineMapSourceBytes=0,inlineMapSourceCount=0;for(auto i:large)if(inlineMaps[nodes[i].name]){inlineMapSourceCount++;inlineMapSourceBytes+=nodes[i].self;}
 // Identify actual operation entries/ancestry, not V8 Context.previous or prototype traversal.
 vector<uint32_t> operationRoots;auto isOperation=[&](uint32_t u){if(nodes[u].type!=3)return false;for(uint32_t j=offset[u];j<offset[u+1];j++)if(edges[j].type==2&&(ename(edges[j])=="previous"||ename(edges[j])=="awaited"))return true;return false;};
 for(auto map:roots["Flight.pendingOperations"])for(uint32_t j=offset[map];j<offset[map+1];j++)if(ename(edges[j])=="table"){auto table=edges[j].to;for(uint32_t j2=offset[table];j2<offset[table+1];j2++)if(strong(table,edges[j2])&&isOperation(edges[j2].to))operationRoots.push_back(edges[j2].to);}
 vector<bool> ancestry(n);vector<uint32_t> operations=operationRoots;for(size_t q=0;q<operations.size();q++){auto u=operations[q];if(ancestry[u])continue;ancestry[u]=true;for(uint32_t j=offset[u];j<offset[u+1];j++)if(edges[j].type==2&&(ename(edges[j])=="previous"||ename(edges[j])=="awaited")&&nodes[edges[j].to].type==3&&!ancestry[edges[j].to])operations.push_back(edges[j].to);}
 uint64_t ancestryCount=count(ancestry.begin(),ancestry.end(),true),restrictedSource=0;vector<bool> restricted(n);vector<uint32_t> todo;for(uint32_t u=0;u<n;u++)if(ancestry[u])todo.push_back(u);
 while(!todo.empty()){auto u=todo.back();todo.pop_back();if(restricted[u])continue;restricted[u]=true;if(counted[u])restrictedSource+=nodes[u].self;for(uint32_t j=offset[u];j<offset[u+1];j++){auto key=ename(edges[j]);if(strong(u,edges[j])&&key!="__proto__"&&key!="prototype"&&key!="constructor"&&key!="native_context"&&!(key=="map"&&edges[j].type==3)&&strings[nodes[edges[j].to].name]!="system / NativeContext")todo.push_back(edges[j].to);}}
 vector<uint64_t> mapDominated(k+1);for(auto i:mapUrls)if(number[i])mapDominated[number[i]]=nodes[i].self;for(uint32_t i=k;i>1;i--)mapDominated[dom[i]]+=mapDominated[i];
 sort(large.begin(),large.end(),[&](auto a,auto b){return nodes[a].self>nodes[b].self;});
 cout<<"{\"graph_policy\":\"STRONG_EDGES_EXCLUDING_WEAK_AND_NONROOT_SHORTCUTS; ephemeron conditionality not simulated\",\"nodes\":"<<n<<",\"edges\":"<<edges.size()<<",\"strong_reachable_nodes\":"<<k<<",\"snapshot_self_bytes\":"<<total<<",\"strong_reachable_bytes\":"<<retained[1]<<",\"large_source_count\":"<<large.size()<<",\"large_source_bytes\":"<<sourceBytes<<",\"large_source_map_url_count\":"<<mapUrls.size()<<",\"large_source_map_url_self_bytes\":"<<mapUrlBytes<<",\"source_strings_with_inline_map_count\":"<<inlineMapSourceCount<<",\"source_strings_with_inline_map_self_bytes\":"<<inlineMapSourceBytes<<",\"flight_ancestry\":{\"map_entry_candidates\":"<<operationRoots.size()<<",\"previous_awaited_nodes\":"<<ancestryCount<<",\"restricted_reachable_source_bytes\":"<<restrictedSource<<",\"policy\":\"own previous/awaited; reach excludes prototype/constructor/native-context/object-shape edges; not exclusive dominance\"},\"type_bytes\":{";bool sep=false;for(auto&[type,bytes]:typeBytes){if(sep)cout<<",";sep=true;cout<<"\""<<type<<"\":"<<bytes;}cout<<"},\"top_dominators\":[";vector<uint32_t> top;for(uint32_t d=2;d<=k;d++)if(nodes[vertex[d]].type!=9&&retained[d]>=1048576)top.push_back(d);sort(top.begin(),top.end(),[&](auto a,auto b){return retained[a]>retained[b];});sep=false;for(size_t z=0;z<min<size_t>(top.size(),20);z++){auto d=top[z];if(sep)cout<<",";sep=true;cout<<"{\"node\":\""<<label(vertex[d])<<"\",\"node_id\":"<<nodes[vertex[d]].id<<",\"retained_bytes\":"<<retained[d]<<",\"source_bytes\":"<<sourceDominated[d]<<"}";}cout<<"],\"mechanisms\":[";sep=false;
 for(auto&[name,rr]:roots){sort(rr.begin(),rr.end());rr.erase(unique(rr.begin(),rr.end()),rr.end());vector<bool> seen(n);vector<uint32_t> todo=rr;uint64_t reachableSource=0;while(!todo.empty()){auto u=todo.back();todo.pop_back();if(seen[u])continue;seen[u]=true;if(counted[u])reachableSource+=nodes[u].self;for(uint32_t j=offset[u];j<offset[u+1];j++)if(strong(u,edges[j]))todo.push_back(edges[j].to);}
  uint64_t dominatedSource=0,dominatedAll=0,dominatedMap=0;set<uint32_t> rootNumbers;for(auto u:rr)if(number[u])rootNumbers.insert(number[u]);for(auto d:rootNumbers){bool covered=false;for(auto a=dom[d];a;a=dom[a])if(rootNumbers.count(a)){covered=true;break;}if(!covered){dominatedSource+=sourceDominated[d];dominatedAll+=retained[d];dominatedMap+=mapDominated[d];}}
  if(sep){cout<<",";}
  sep=true;cout<<"{\"name\":\""<<name<<"\",\"root_count\":"<<rr.size()<<",\"reachable_source_bytes\":"<<reachableSource<<",\"dominated_source_bytes\":"<<dominatedSource<<",\"dominated_map_url_bytes\":"<<dominatedMap<<",\"dominated_all_bytes\":"<<dominatedAll<<"}";
 }
 cout<<"],\"source_origins\":[";sep=false;for(auto&[origin,ids]:originStrings){uint64_t bytes=0;for(auto id:ids)bytes+=nodes[id].self;if(sep)cout<<",";sep=true;cout<<"{\"origin\":\""<<origin<<"\",\"script_count\":"<<originScripts[origin]<<",\"unique_sources\":"<<ids.size()<<",\"source_bytes\":"<<bytes<<"}";}
 cout<<"],\"largest_source_strings\":[";sep=false;for(size_t z=0;z<min<size_t>(large.size(),20);z++){auto u=large[z];if(sep)cout<<",";sep=true;auto d=number[u]?dom[number[u]]:0;cout<<"{\"node_id\":"<<nodes[u].id<<",\"snapshot_name_chars\":"<<stringChars[nodes[u].name]<<",\"self_bytes\":"<<nodes[u].self<<",\"immediate_dominator\":\""<<(d?label(vertex[d]):"UNREACHABLE")<<"\",\"dominator_chain\":[";bool ds=false;for(auto a=d,depth=0u;a&&depth<30;a=dom[a],depth++){if(ds)cout<<",";ds=true;cout<<"{\"node\":\""<<label(vertex[a])<<"\",\"retained_bytes\":"<<retained[a]<<",\"source_bytes\":"<<sourceDominated[a]<<"}";}cout<<"],\"path\":[";vector<uint32_t> path;auto t=u;while(t&&bfsParent[t]!=UINT32_MAX&&path.size()<80){path.push_back(t);t=bfsParent[t];}reverse(path.begin(),path.end());bool ss=false;for(size_t q=0;q<min<size_t>(path.size(),30);q++){t=path[q];auto e=bfsEdge[t];auto key=e==UINT32_MAX?"root":ename(edges[e]);if(!edgeLabels.count(key)&&key!="[index]"&&!(details&&key.size()<80&&key.find_first_not_of("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$ .") == string::npos))key="<edge>";if(ss)cout<<",";ss=true;cout<<"{\"via\":\""<<key<<"\",\"edge_type\":\""<<(e==UINT32_MAX?"root":edgeTypes[edges[e].type])<<"\",\"node\":\""<<label(t)<<"\"}";}cout<<"]}";}cout<<"]}"<<endl;
 }catch(...){cerr<<"Snapshot analysis refused: invalid private input, schema or resource budget."<<endl;return 1;}}
